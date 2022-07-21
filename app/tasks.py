"""Tasks module, specifying Hazen-related tasks and utilities."""

import os

from flask import current_app, flash, jsonify
from app.models import Task, Report

from hazen import worker


@worker.task(bind=True)
def produce_report(self, task_name, image_files, user_id, series_id):
    # import Hazen functionality
    task = __import__(f'hazenlib.{task_name}', globals(), locals(), [f'{task_name}'])
    current_app.logger.info(f"Producing report from {task.__name__}")

    # Perform analysis/task
    self.update_state(state='IN PROGRESS')
    # Perform task and generate result
    result = task.main(data=image_files)
    print(result)
    self.update_state(state='STORING RESULTS')
    # Store analysis result in database
    report = Report(
        hazen_version="1", data=result,
        user_id=user_id, series_id=series_id,
        task_name=task_name)
    # Save information to database
    report.save()
    flash(f'Completed processing: {task_name}')
    return jsonify(report.data)
