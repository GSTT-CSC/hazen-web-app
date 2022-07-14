import os
import shutil
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import pydicom.errors

from app import db
from app.main import bp
from app.main.forms import AcquisitionForm
from app.models import User, Acquisition, ProcessTask


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# Homepage
# Overview of process tasks that can be performed
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # list available tasks that can be performed
    tasks = ProcessTask.query.all()

    return render_template('index.html', title='Home', tasks=tasks)


class SeriesExistsError(Exception): pass


# Dashboard
# authenticated users can overview and perform tasks/analysis on files they uploaded
@bp.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard():
    # locate user in db by username
    user = User.query.filter_by(username=current_user.username).first_or_404()
    # # list available tasks that can be performed
    # tasks = ProcessTask.query.all()

    if request.method == 'POST': # form.validate_on_submit()
        for key, file in request.files.items():
            """
            for file in files:
                if file and allowed_file(file.filename):
            """

            if key.startswith('file'):
                filename = secure_filename(file.filename)
                secure_path = os.path.join(current_app.config['UPLOADED_PATH'], filename)
                file.save(secure_path)

                try:
                    filesystem_dir = ingest(secure_path)
                except SeriesExistsError:
                    os.remove(secure_path)
                    flash('SeriesInstanceUID already exists!')
                    return redirect(url_for('main.dashboard'))

                permanent_path = os.path.join(filesystem_dir, filename)

                shutil.move(secure_path, permanent_path)
                flash('Upload success!')

        return redirect(url_for('main.dashboard'))

    # Display list of available acquisitions
    page = request.args.get('page', 1, type=int)
    acquisitions = user.acquisitions.order_by(Acquisition.created_at.desc()).paginate(
        page, current_app.config['ACQUISITIONS_PER_PAGE'], False)
    next_url = url_for('main.dashboard', page=acquisitions.next_num) \
        if acquisitions.has_next else None
    prev_url = url_for('main.dashboard', page=acquisitions.prev_num) \
        if acquisitions.has_prev else None

    return render_template('user.html', title='Acquisitions', # , tasks=tasks
        acquisitions=acquisitions.items, next_url=next_url, prev_url=prev_url)


# Upload acquisitions and parse metadata from DICOM header
def ingest(file_path):
    try:
        dcm: pydicom.Dataset = pydicom.read_file(file_path)
        # TODO: parse additional fields from DICOM 
        series_instance_uid = dcm.SeriesInstanceUID
        description = f"{dcm.StudyDescription}: {dcm.SeriesDescription}"
        filename = os.path.basename(file_path)
        files = 1

        # TODO: allow multiple files with the same series ID
        if Acquisition.query.filter_by(series_instance_uid=series_instance_uid).first():
            current_app.logger.info('series exists')
            raise SeriesExistsError(f"UID: {series_instance_uid}")

        # Create new row in Acquisitions table
        acq = Acquisition(series_instance_uid=series_instance_uid,
                          files=files,
                          description=description,
                          filename=filename,
                          user_id=current_user.get_id())
        acq.save()

        # Maybe change location allocation of where uploaded files are stored
        user = User.query.get(current_user.get_id())
        directory = os.path.join(current_app.config['UPLOADED_PATH'], user.filesystem_key, acq.filesystem_key)
        os.makedirs(directory, exist_ok=True)
        flash('File(s) successfully uploaded')

        return directory

    except Exception as e:
        raise

@bp.route('/user/<username>/<acquisition_uuid>/')
@login_required
def delete_acq(username, acquisition_uuid):
    user = User.query.get(current_user.get_id())
    acquisition = Acquisition.query.filter_by(id=acquisition_uuid, user_id=user.id)

    # delete files
    directory = os.path.join(current_app.config['UPLOADED_PATH'], user.filesystem_key, acquisition.first().filesystem_key)
    shutil.rmtree(directory)

    # remove db entry
    acquisition.delete()
    db.session.commit()

    return redirect(request.referrer)
