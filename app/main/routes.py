import os
import shutil
from datetime import datetime

import pydicom.errors
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.main import bp
from app.models import User, Image, Series, Study, Task


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


# Workbench?
# authenticated users can overview and perform tasks/analysis on uploaded files 
@bp.route('/workbench/', methods=['GET', 'POST'])
@login_required
def workbench():
    # Display available tasks that can be performed
    tasks = Task.query.all()

    # Display available image Series
    page = request.args.get('page', 1, type=int)
    acquisitions = Series.query.filter_by(user_id=current_user.id).paginate(
        page, current_app.config['ACQUISITIONS_PER_PAGE'], False)
    # user.series.order_by(Series.created_at.desc()).paginate(
    #     page, current_app.config['ACQUISITIONS_PER_PAGE'], False)
    next_url = url_for('main.workbench', page=acquisitions.next_num) \
        if acquisitions.has_next else None
    prev_url = url_for('main.workbench', page=acquisitions.prev_num) \
        if acquisitions.has_prev else None

    if request.method == 'POST': # form.validate_on_submit()
        for key, file in request.files.items():
            if key.startswith('file'):
                filename = secure_filename(file.filename)
                secure_path = os.path.join(current_app.config['UPLOADED_PATH'], filename)
                file.save(secure_path)

                try:
                    filesystem_dir = ingest(secure_path)
                except ImageExistsError:
                    os.remove(secure_path)
                    flash('Images have already been uploaded!', 'danger')
                    return redirect(url_for('main.workbench'))

                permanent_path = os.path.join(filesystem_dir, filename)
                shutil.move(secure_path, permanent_path)
                flash('Files uploaded successfully!', 'success')
        return redirect(url_for('main.workbench'))

    return render_template('workbench.html', title='Workbench', tasks=tasks,
        acquisitions=acquisitions.items, next_url=next_url, prev_url=prev_url)


# Upload images one at a time and parse metadata from DICOM header
def ingest(file_path):
    try:
        # Load in the DICOM header into a pydicom Dataset
        dcm: pydicom.Dataset = pydicom.read_file(file_path, stop_before_pixels=True)

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


# Delete acquisitions
@bp.route('/user/<acquisition_uuid>/')
@login_required
def delete_acq(acquisition_uuid):
    user = User.query.get(current_user.get_id())
    acquisition = Acquisition.query.filter_by(id=acquisition_uuid, user_id=user.id)

    # delete files
    directory = os.path.join(current_app.config['UPLOADED_PATH'], user.filesystem_key, acquisition.first().filesystem_key)
    shutil.rmtree(directory)

    # remove db entry
    acquisition.delete()
    db.session.commit()

    return redirect(request.referrer)


# Reports dashboard
# Trend monitoring and overview of reports
@bp.route('/reports/', methods=['GET', 'POST'])
@login_required
def reports():
    return redirect(url_for('main.index'))
