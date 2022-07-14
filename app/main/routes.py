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


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    tasks = ProcessTask.query.all()
    page = request.args.get('page', 1, type=int)

    acquisitions = user.acquisitions.order_by(Acquisition.created_at.desc()).paginate(
        page, current_app.config['ACQUISITIONS_PER_PAGE'], False)

    next_url = url_for('main.user', username=user.username, page=acquisitions.next_num) \
        if acquisitions.has_next else None
    prev_url = url_for('main.user', username=user.username, page=acquisitions.prev_num) \
        if acquisitions.has_prev else None

    return render_template('user.html', user=user, acquisitions=acquisitions.items,
                           next_url=next_url, prev_url=prev_url, tasks=tasks)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    acquisitions = Acquisition.query.order_by(Acquisition.created_at.desc()).paginate(
        page, current_app.config['ACQUISITIONS_PER_PAGE'], False)

    next_url = url_for('main.explore', page=acquisitions.next_num) \
        if acquisitions.has_next else None
    prev_url = url_for('main.explore', page=acquisitions.prev_num) \
        if acquisitions.has_prev else None

    return render_template("index.html", title='Explore', acquisitions=acquisitions.items, next_url=next_url,
                           prev_url=prev_url)


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
