import os
import sys
import importlib
from flask import render_template, flash, request, jsonify, url_for, current_app
from flask_login import current_user, login_required
from app.reports import bp
from app.reports.forms import ProcessTaskForm
from app.models import Image, Series, Study, Task, Report


@bp.route('/report/<acquisition_id>',  methods=['GET', 'POST'])
@login_required
def report(acquisition_id, pending_id=None):
    series = Series.query.filter_by(id=acquisition_id).first_or_404()
    from app.tasks import produce_report

    if request.method == 'GET':

        form = ProcessTaskForm()
        tasks = [(x.name, x.name) for x in Task.query.all()]
        form.process_task_name.choices = tasks

        if pending_id:
            pending = produce_report.AsyncResult(pending_id)
        else:
            pending = None

        reports = Report.query.filter_by(series_id=series.id).all()
        if not reports:
            flash(f'No reports found for {series.id.hex}', 'danger')

        return render_template('report.html',
                               form=form,
                               acquisition=series,
                               reports=reports,
                               tasks=tasks,
                               pending=pending)

    elif request.method == 'POST':
        # Identify selected task
        task_name = request.form['process_task_name']
        current_app.logger.info(task_name)
        current_app.logger.info(f"Performing {task_name} task on {series.description}")

        # Select files to perform task on
        folder = os.path.join(current_app.config['UPLOADED_PATH'],
                                        series.filesystem_key)
        image_files = [os.path.join(folder, file) for file in os.listdir(folder)]

        # Ensure that appropriate number of files were selected
        series_files = Image.query.filter_by(series_id=acquisition_id).count()
        print(series_files)
        if len(image_files) != series_files:
            raise Exception('Number of dicoms in directory not equal to expected!')

        flash(f'Starting process: {task_name}', 'info')
        celery_job = produce_report.delay(task_name=task_name, user_id=current_user.id, image_files=image_files, series_id=series.id)
        current_app.logger.info(f"Task performed successfully!")
        flash(f'Completed processing: {task_name}')
        current_app.logger.info(celery_job)

        return url_for('reports.report', acquisition_id=series.id, pending=celery_job.id)
