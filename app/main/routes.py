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
from app.main.forms import ImageUploadForm, ProcessTaskForm, BatchProcessingForm
from app.models import Image, Series, Study, Device, Task, Report

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


class ImageExistsError(Exception): pass


def upload_file(file):
    filename = secure_filename(file.filename)
    secure_path = os.path.join(current_app.config['UPLOADED_PATH'], filename)
    try:
        file.save(secure_path)
    except IsADirectoryError:
        flash("No files were selected", 'info')
        return redirect(url_for('main.workbench'))

    try:
        filesystem_dir = ingest(secure_path)
        permanent_path = os.path.join(filesystem_dir, filename)
        shutil.move(secure_path, permanent_path)
        flash(f'{filename} file has been uploaded successfully!', 'success')
    except ImageExistsError:
        os.remove(secure_path)
        flash(f'{filename} file has already been uploaded!', 'danger')


# Upload images one at a time and parse metadata from DICOM header
def ingest(file_path):
    try:
        # Load in the DICOM header into a pydicom Dataset
        dcm = pydicom.read_file(file_path, force=True,
                                                stop_before_pixels=True)

        # Parse the relevant fields into variables
        image_uid = dcm.SOPInstanceUID
        series_uid = dcm.SeriesInstanceUID
        study_uid = dcm.StudyInstanceUID
        description = f"{dcm.StudyDescription}: {dcm.SeriesDescription}"
        filename = os.path.basename(file_path)

        # Ensure that image is not yet in database
        image_exists = db.session.query(db.exists().where(Image.uid == image_uid)).scalar()
        if image_exists:
            current_app.logger.info('Image already exists in database')
            raise ImageExistsError(f"UID: {image_uid}")

        # Collect relevant pieces of information from DICOM header
        # 0020 Study date
        study_date = dcm.StudyDate
        # (0008,0020)	DA	Study Date	
        # (0008,0021)	DA	Series Date	
        # (0008,0022)	DA	Acquisition Date
        # 0030 study time
        study_time = dcm.StudyTime
        # (0008,0030)	TM	Study Time	
        # (0008,0031)	TM	Series Time	
        # (0008,0032)	TM	Acquisition Time
        institution = dcm.InstitutionName
        # 0070 manufacturer
        manufacturer = dcm.Manufacturer
        # (0008,1090)	LO	Manufacturer's Model Name
        model = dcm[0x00081090].value
        station_name = dcm.StationName
        # 0050 accession number
        accession_number = dcm.AccessionNumber
        # print({"institution": institution,
        #        "manufacturer": manufacturer,
        #        "model": model,
        #        "study_date": study_date,
        #        "study_time": study_time,
        #        "station_name": station_name,
        #        "accession_number": accession_number
        #        })

        # Save the image data into the corresponding tables:
        
        # 0. Device:
        device_exists = db.session.query(db.exists(
            ).where(Device.institution == institution
            ).where(Device.manufacturer == manufacturer
            ).where(Device.device_model == model
            ).where(Device.station_name == station_name)).scalar()
        if not device_exists:
            new_device = Device(
                institution=institution, manufacturer=manufacturer,
                device_model=model, station_name=station_name)
            new_device.save()
        device_id = Device.query.where(Device.institution == institution
            ).where(Device.manufacturer == manufacturer
            ).where(Device.device_model == model
            ).where(Device.station_name == station_name).first().id
        #TODO remove in production
        print("device id:", device_id)
        
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

            new_series = Series(
                uid=series_uid, description=dcm.SeriesDescription, user_id=current_user.get_id(), device_id=device_id,
                study_id=study_id, series_datetime=series_datetime)
            new_series.save()
        series_id = Series.query.filter_by(uid=series_uid).first().id
        #TODO remove in production
        print("series id:", series_id)

        # 3. Image:
        new_image = Image(
            uid=image_uid, series_id=series_id, filename=filename,
            accession_number=accession_number)
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

    # Create Choose file form
    upload_form = ImageUploadForm()

    # List available tasks that can be performed
    tasks = Task.query.all()
    batch_form = BatchProcessingForm()
    batch_form.task_name.choices = [task.name for task in tasks]

    if request.method == 'POST':
        if 'file' in request.files.keys():
            # Uploaded by DropZone
            dropzone_file = request.files['file']
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

    return render_template('workbench.html', title='Workbench', studies=studies,
            upload_form=upload_form, batch_form=batch_form # , tasks=tasks,
        )
    # , series=series, next_url=next_url, prev_url=prev_url


def locate_image_files(filesystem_key):
    # Select files in series folder
    folder = os.path.join(current_app.config['UPLOADED_PATH'],
                                    filesystem_key)
    image_files = [os.path.join(folder, file) for file in os.listdir(folder)]
    return image_files


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


# Select task to be run on (image) series
@bp.route('/task_selection/<series_id>/', methods=['GET', 'POST'])
@login_required
def task_selection(series_id):
    # Retrieve the Series that was selected
    series = Series.query.filter_by(id=series_id).first_or_404()

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

