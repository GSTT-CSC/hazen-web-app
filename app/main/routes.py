import os
import shutil
from datetime import datetime
from importlib.metadata import version

from flask import current_app, render_template, request, redirect
from flask import send_from_directory, url_for, session, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import pydicom.errors

from app import db
from app.main import bp
from app.main.forms import ImageUploadForm, ProcessTaskForm, BatchProcessingForm
from app.models import Image, Series, Study, Device, Task, Report
from app.util.im2db_utils import upload_file, locate_image_files

hazenlib_version = version('hazen')

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# Homepage
# Overview of process tasks that can be performed
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
# @login_required
def index():
    # list available tasks that can be performed
    tasks = Task.query.all()

    return render_template('index.html', title='Home', tasks=tasks)


# Delete or archive series, delete reports
@bp.route('/delete/')
@login_required
def delete(series_id=None, report_id=None):
    """Generic delete function

    Args:
        series_id (optional): Database ID of a Series row. Defaults to None.
        report_id (optional): Database ID of a Reports row. Defaults to None.

    Returns:
        updates database table to reflect deletion
    """
    if 'series_id' in request.args.keys():
        # Get series_id from URL, find series in Table
        series_id = request.args['series_id']
        series = Series.query.filter_by(id=series_id).first_or_404()
        # Check whether reports were made for that series_id
        if series.has_report:
            # If series already has reports, archive series but don't delete
            series.update(archived=True)
            flash(f"Series {series.description} was archived as it already has reports.", 'info')
        else:
            # If there are no reports associated, then delete all files
            # from filesystem
            series_folder = os.path.join(current_app.config['UPLOADED_PATH'], series.filesystem_key)
            try:
                shutil.rmtree(series_folder)
            except Exception as e:
                flash(f"Could not find files under this series_id folder")
                print(e)
                raise e
            # from database
            images = Image.query.filter_by(series_id=series_id).all()
            for image in images:
                image.delete()
            # Check whether study has other series, delete if not
            additional_series = Study.query.filter_by(id=series.study_id).count()
            if additional_series == 1:  # study only had this series
                study = Study.query.filter_by(id=series.study_id).first_or_404()
                study.delete()
            # Lastly, delete the series itself from the DB
            series.delete()
            flash(f"All files in series {series.description} were deleted as it has no reports.", 'info')
        db.session.commit()

    if 'report_id' in request.args.keys():
        # Get report_id from URL, find report in Table
        report_id = request.args['report_id']
        report = Report.query.filter_by(id=report_id).first_or_404()
        # Check whether series has other reports or is this the only one
        additional_reports = Report.query.filter_by(series_id=report.series_id).count()
        if additional_reports > 1:  # series has other reports 
            # delete selected one
            report.delete()
        else:  # series only had this report
            # delete selected one
            report.delete()
            # and update has_report field of the series
            series = Series.query.filter_by(id=report.series_id).first_or_404()
            # Reset series bool so it is displayed without a report on the workbench
            series.update(has_report=False, archived=False)
        db.session.commit()
        flash(f"Report was deleted.", 'info')

    return redirect(request.referrer)


# Workbench
# authenticated users can overview and perform tasks/analysis on uploaded files 
@bp.route('/workbench/', methods=['GET', 'POST'])
@login_required
def workbench():
    # Save current user's ID to Session
    session['current_user_id'] = current_user.id

    # Display available image Series, grouped by Study UID
    studies = db.session.query(Study).order_by(Study.created_at.desc())
    # Collect device information about studies for display
    study_device_list = [{"study": study,
                        "device": study.series[0].devices
                        } for study in studies]

    # Create Choose file form
    upload_form = ImageUploadForm()

    # List available tasks that can be performed
    tasks = Task.query.all()
    batch_form = BatchProcessingForm()
    batch_form.task_name.choices = [task.name for task in tasks]

    if request.method == 'POST':
        if 'file' in request.files.keys():
            # Uploaded by DropZone
            dropzone_file = request.files.get('file')
            if dropzone_file.filename.split(".")[-1].lower() not in current_app.config['ALLOWED_EXTENSIONS']:
                return 'incorrect file type', 400
            upload_file(dropzone_file)

        elif 'submit' in request.form.keys():
            # Batch processing functionality
            if request.form['submit'] == 'Run task on selected series':
                # Initialise variables for batch processing
                task_name = ""
                selected_series = []
                # Load which series were selected for which task
                try:
                    task_name = request.form['task_name']
                    task_variable = request.form['task_variable']
                    selected_series = request.form.getlist('many_series')
                except Exception as e:
                    flash(f'No task or image series were selected.', 'info')
                    return redirect(url_for('main.workbench'))

                if len(selected_series) == 0:
                    flash(f"No image series were selected for {task_name} task.", 'info')
                    return redirect(url_for('main.workbench'))

                # Create Celery jobs from batch processing request
                celery_job_list = create_celery_jobs(
                    user_id=current_user.id, series_ids=selected_series,
                    task_name=task_name, task_variable=task_variable)
                job_ids = [job.id for job in celery_job_list]
                msg = 'The following jobs have been queued: ' + ",".join(job_ids)
                current_app.logger.info(msg)
                flash(f"Processing of the {task_name} task has begun for {len(selected_series)} series", "success")

            # Upload file functionality
            else:
                # Uploaded by Choose File
                for choose_file in request.files.getlist('image_files'):
                    upload_file(choose_file)

        return redirect(url_for('main.workbench'))

    return render_template('workbench.html', title='Workbench',
            study_device_list=study_device_list,
            upload_form=upload_form, batch_form=batch_form # , tasks=tasks,
        )
    # , series=series, next_url=next_url, prev_url=prev_url


def create_celery_jobs(user_id, task_name: str, series_ids: list, task_variable=None):
    celery_job_list = []
    from app.tasks import produce_report
    # Check which task is requested
    if task_name == 'snr':
        if len(series_ids) < 2 or (len(series_ids) % 2) != 0:
            flash("Incorrect number of image series selected for SNR measurement", 'info')
        else:
            #TODO currently it is assumed that a single pair of images are selected
            image_files = []
            for series_id in series_ids:
                # Identify selected series
                series = Series.query.filter_by(id=series_id).first_or_404()
                image_files.extend(locate_image_files(series.filesystem_key))
            current_app.logger.info(f"Performing {task_name} task on all images within series {series_ids}")
            celery_job = produce_report.delay(
                user_id=user_id, series_id=series_ids[0], task_name=task_name,
                image_files=image_files)
            celery_job_list.append(celery_job)
    else:
        # Set off a job per series
        for series_id in series_ids:
            # Identify selected series
            series = Series.query.filter_by(id=series_id).first_or_404()
            image_files = locate_image_files(series.filesystem_key)
            # Set off task processing as a Celery job
            current_app.logger.info(f"Performing {task_name} task on {len(image_files)} images within the {series_id} series")
            celery_job = produce_report.delay(
                user_id=user_id, series_id=series_id, task_name=task_name,
                image_files=image_files)
            celery_job_list.append(celery_job)
    return celery_job_list

# Series overview
# Description, existing reports and run new tasks
@bp.route('/series/<series_id>', methods=['GET', 'POST'])
@login_required
def series_view(series_id):
    user_id = current_user.id
    # Retrieve the Series that was selected
    series = Series.query.filter_by(id=series_id).first_or_404()

    if request.method == 'GET':
        # Prepare the form to accept task selection
        form = ProcessTaskForm()
        # Provide list of available tasks that can be performed
        form.task_name.choices = [(task.name, task.name) for task in Task.query.all()]
        series_files = Image.query.filter_by(series_id=series_id).count()

        # Store information about this series in a dict that can be passed to the html
        series_dict = {
            'description': series.description,
            'series_datetime': series.series_datetime,
            'created_at': series.created_at,
            'series_files': Image.query.filter_by(series_id=series_id).count(),
            'has_report': series.has_report
        }

        # Identify reports made for that series_id
        reports = db.session.query(Report).filter_by(
                        series_id=series_id).order_by(Report.created_at.desc())
        #, user_id=user_id
        # TODO: add user restriction later

        # if len(reports.all()) < 1:
        #     print("No reports available for this user")
        # else:

        # Group results by task_name --> dict { task: [results] }
        results_dict = {}
        tasks = [report.task_name for report in reports]
        for task in tasks:
            task_result = Report.query.filter_by( #user_id=user_id,
                                    series_id=series_id, task_name=task
                                    ).first_or_404()
            # Find report images for series + task
            # directory = os.path.join(current_app.config['UPLOADED_PATH'],
            #                             )
            image_files = locate_image_files(
                            task_result.filesystem_key, filename=True)
            # Store values in dict to be displayed
            results_dict[task] = {
                "measurement": task_result.data,
                "created": task_result.created_at,
                "directory": task_result.filesystem_key,
                "image_files": image_files,
                "width": 100 / len(image_files) -1
            }

        return render_template('series_view.html', title='Series overview',
                        form=form, series=series_dict, results=results_dict,
                        hazenlib_version=hazenlib_version)

    if request.method == 'POST':
        # Set off task processing as a Celery job
        # Unpack variables from session
        task_name = request.form['task_name']
        task_variable = request.form['task_variable']
        user_id = session['current_user_id']
        # Select files to perform task on
        folder = os.path.join(current_app.config['UPLOADED_PATH'],
                                        series.filesystem_key)
        image_files = [os.path.join(folder, file) for file in os.listdir(folder)]

        # Ensure that appropriate number of files were selected
        series_files = Image.query.filter_by(series_id=series.id).count()
        if len(image_files) != series_files:
            raise Exception('Number of files in directory is not equal to expected!')

        # Create Celery jobs from processing request
        current_app.logger.info(f"Performing {task_name} task on {series.description}")
        celery_job_list = create_celery_jobs(
            user_id=current_user.id, series_ids=[series.id],
            task_name=task_name, task_variable=task_variable)

        current_app.logger.info(f"Task performed successfully! \n")
        flash(f'Completed {task_name} measurement!', 'info')

        # Passing task and series information to next page via Session dict
        session['task_name'] = task_name
        session['series_id'] = series_id

        return redirect(url_for('main.series_view', series_id=series_id))


    return render_template('result.html', title='Result',
                form=form,
                series=series_dict, results=results_dict)


# Reports dashboard
# Overview of reports
#TODO: Trend monitoring dashboards
@bp.route('/reports/', methods=['GET', 'POST'])
@login_required
def reports():
    # Display existing reports
    reports = db.session.query(Report).order_by(Report.created_at.desc())

    # Display reports in a table
    page = request.args.get('page', 1, type=int)
    reports_pages = reports.paginate(
    page, current_app.config['ACQUISITIONS_PER_PAGE'], False)
    next_url = url_for('main.reports', page=reports_pages.next_num) \
        if reports_pages.has_next else None
    prev_url = url_for('main.reports', page=reports_pages.prev_num) \
        if reports_pages.has_prev else None

    return render_template('reports.html', title="Reports",
        reports=reports_pages.items, next_url=next_url, prev_url=prev_url)

