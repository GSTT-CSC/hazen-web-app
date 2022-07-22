"""Tasks module, specifying Hazen-related tasks and utilities."""

import importlib
import inspect
import sys
from importlib.metadata import version

from flask import current_app, jsonify, make_response

from app.models import Report
from hazen import worker


@worker.task(bind=True)
def produce_report(self, task_name, image_files, user_id, series_id):
    # import Hazen functionality
    task_module = importlib.import_module(f"hazenlib.tasks.{task_name}")
    class_list = [cls for _, cls in inspect.getmembers(sys.modules[task_module.__name__], lambda x: inspect.isclass(x) and (x.__module__ == task_module.__name__))]
    if len(class_list) > 1:
        raise Exception(f'Task {task_module} has multiple class definitions: {class_list}')
    task = getattr(task_module, class_list[0].__name__)(data_paths=image_files, report=True)

    current_app.logger.info(f"Producing report from {task.__class__.__name__}")

    # Perform analysis/task
    self.update_state(state='IN PROGRESS')
    # Perform task and generate result
    result = task.run()
    self.update_state(state='STORING RESULTS')
    # Store analysis result in database
    report = Report(
        hazen_version=version('hazen'), data=result,
        user_id=user_id, series_id=series_id,
        task_name=task_name)
    # Save information to database
    report.save()
    return make_response(jsonify(dict(report.data)), 200)
