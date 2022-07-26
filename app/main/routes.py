import os
import shutil
from datetime import datetime
from importlib.metadata import version

from flask import current_app, render_template, redirect, url_for, request, session, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import pydicom.errors

from app import db
from app.main import bp
from app.main.forms import ImageUploadForm, ProcessTaskForm
from app.models import User, Image, Series, Study, Device, Institution, Task, Report


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


class ImageExistsError(Exception): pass


# Workbench
# authenticated users can overview and perform tasks/analysis on uploaded files 
@bp.route('/workbench/', methods=['GET', 'POST'])
@login_required
def workbench():
    # Save current user's ID to Session
    session['current_user_id'] = current_user.id

    # Display available image Series
    page = request.args.get('page', 1, type=int)
    series = db.session.query(Series).filter_by(user_id=current_user.id, archived=False).order_by(Series.created_at.desc()).paginate(
        page, current_app.config['ACQUISITIONS_PER_PAGE'], False)

    next_url = url_for('main.workbench', page=series.next_num) \
        if series.has_next else None
    prev_url = url_for('main.workbench', page=series.prev_num) \
        if series.has_prev else None

    #TODO: for batch processing in the future, will need to have the list of
    # available tasks that can be performed
    tasks = Task.query.all()
    
    form = ImageUploadForm()

    if request.method == 'POST': # form.validate_on_submit()
        for key, file in request.files.items():
            # Uploaded by DropZone       Uploaded by Choose File
            if key.startswith('file') or key.startswith('image_file'):
                filename = secure_filename(file.filename)
                secure_path = os.path.join(current_app.config['UPLOADED_PATH'], filename)
                file.save(secure_path)

                try:
                    filesystem_dir = ingest(secure_path)
                except ImageExistsError:
                    os.remove(secure_path)
                    flash(f'{filename} file has already been uploaded!', 'danger')
                    return redirect(url_for('main.workbench'))

                permanent_path = os.path.join(filesystem_dir, filename)
                shutil.move(secure_path, permanent_path)
                flash('Files uploaded successfully!', 'success')
        return redirect(url_for('main.workbench'))

    return render_template('workbench.html', title='Workbench', form=form, # tasks=tasks,
        series=series.items, next_url=next_url, prev_url=prev_url)


# Upload images one at a time and parse metadata from DICOM header
def ingest(file_path):
    try:
        # Load in the DICOM header into a pydicom Dataset
        dcm = pydicom.read_file(file_path, force=True,
                                                stop_before_pixels=True)

        # Parse the relevant fields into variables
        series_uid = dcm.SeriesInstanceUID
        study_uid = dcm.StudyInstanceUID
        image_uid = dcm.SOPInstanceUID
        description = f"{dcm.StudyDescription}: {dcm.SeriesDescription}"
        filename = os.path.basename(file_path)

        # Ensure that image is not yet in database
        image_exists = db.session.query(db.exists().where(Image.uid == image_uid)).scalar()
        if image_exists:
            current_app.logger.info('Image already exists in database')
            raise ImageExistsError(f"UID: {image_uid}")

        # Save the image data into the corresponding tables:
        # 0. Device:
        #TODO parse device and manufacturer information from DICOM to db
        
        # 1. Study:
        study_exists = db.session.query(db.exists().where(Study.uid == study_uid)).scalar()
        if not study_exists:
            new_study = Study(uid=study_uid, description=dcm.StudyDescription)
            new_study.save()
        study_id = Study.query.filter_by(uid=study_uid).first().id
        #TODO remove in production
        print("study id:", study_id)
        
        # 2. Series:
        series_exists = db.session.query(db.exists().where(Series.uid == series_uid)).scalar()
        if not series_exists:
            series_time = dcm.SeriesTime.split('.')[0]
            series_datetime = datetime.strptime("-".join([dcm.SeriesDate,series_time]), '%Y%m%d-%H%M%S')
            new_series = Series(uid=series_uid, description=dcm.SeriesDescription, user_id=current_user.get_id(), study_id=study_id, series_datetime=series_datetime)
            new_series.save()
        series_id = Series.query.filter_by(uid=series_uid).first().id
        #TODO remove in production
        print("series id:", series_id)

        # 3. Image:
        new_image = Image(uid=image_uid, series_id=series_id, filename=filename, header=dcm.to_json_dict())
        new_image.save()
        #TODO remove in production
        print("new image id:", new_image.id)

        # Commit all changes to the database
        db.session.commit()

        # Store file in series/image folder
        series_folder = Series.query.filter_by(uid=series_uid).first().filesystem_key
        directory = os.path.join(current_app.config['UPLOADED_PATH'], series_folder)
        os.makedirs(directory, exist_ok=True)

        return directory

    except Exception as e:
        raise


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
            shutil.rmtree(series_folder)
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
            series.update(has_report=False)
        db.session.commit()
        flash(f"Report was deleted.", 'info')

    return redirect(request.referrer)


# Select task to be run on (image) series
@bp.route('/task_selection/<series_id>/', methods=['GET', 'POST'])
@login_required
def task_selection(series_id):
    # Retrieve the Series that was selected
    series = Series.query.filter_by(id=series_id).first_or_404()
    hazenlib_version = version('hazen')

    if request.method == 'GET':
        # Prepare the form to accept task selection
        form = ProcessTaskForm()
        # Provide list of available tasks that can be performed
        form.task_name.choices = [(task.name, task.name) for task in Task.query.all()]
        series_files = Image.query.filter_by(series_id=series_id).count()
        
        return render_template('task_selection.html', title='Select Task',
                        form=form, series=series, series_files=series_files,
                        hazenlib_version=hazenlib_version)

    if request.method == 'POST':
        # Set off task processing as a Celery job
        from app.tasks import produce_report

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

        # Set off task processing as a Celery job
        current_app.logger.info(f"Performing {task_name} task on {series.description}")
        print("debug")
        celery_job = produce_report.delay(
            user_id=user_id, series_id=series.id, task_name=task_name,
            image_files=image_files, slice_width=task_variable)

        current_app.logger.info(f"Task performed successfully! \n")
        flash(f'Completed {task_name} measurement!', 'info')

        # Passing task and series information to next page via Session dict
        session['task_name'] = task_name
        session['series_id'] = series_id

        return redirect(url_for('main.result'))


# Select task to be run on (image) series
@bp.route('/result/', methods=['GET', 'POST'])
@login_required
def result():
    # Retrieve the Task and Series that were selected to create the report
    task_name = session['task_name']
    series_id = session['series_id']
    series = Series.query.filter_by(id=series_id).first_or_404()
    series_files = Image.query.filter_by(series_id=series.id).count()

    # Retrieve the report that was created
    user_id = current_user.id
    report = Report.query.filter_by(
        user_id=user_id, series_id=series_id, task_name=task_name
        ).first_or_404()
    return render_template('result.html', title='Result', results=report.data,
                    task=task_name, series=series, series_files=series_files)


# Reports dashboard
# Overview of reports
#TODO: Trend monitoring dashboards
@bp.route('/reports/', methods=['GET', 'POST'])
@login_required
def reports(series_id=None):
    series_dict = {}
    # Display existing reports
    if request.method == 'GET':
        # If coming from the Workbench with a series_id specified,
        # then display reports made for that series_id
        if 'series_id' in request.args.keys():
            # Get series_id from URL
            series_id = request.args['series_id']
            # Identify reports made for that series_id
            reports = db.session.query(Report).filter_by(series_id=series_id).order_by(Report.created_at.desc())
            # Store information about this series in a dict that can be passed to the html
            series = Series.query.filter_by(id=series_id).first_or_404()
            series_dict = {
                'filtered': True,
                'description': series.description,
                'series_datetime': series.series_datetime,
                'created_at': series.created_at,
                'series_files': Image.query.filter_by(series_id=series_id).count()
            }
            
        # Otherwise display all reports
        else:
            reports = db.session.query(Report).order_by(Report.created_at.desc())
            series_dict['filtered'] = False

        # Display reports in a table
        page = request.args.get('page', 1, type=int)
        reports_pages = reports.paginate(
        page, current_app.config['ACQUISITIONS_PER_PAGE'], False)
        next_url = url_for('main.reports', page=reports_pages.next_num) \
            if reports_pages.has_next else None
        prev_url = url_for('main.reports', page=reports_pages.prev_num) \
            if reports_pages.has_prev else None

    return render_template('reports.html', title="Reports", series=series_dict,
        reports=reports_pages.items, next_url=next_url, prev_url=prev_url)

