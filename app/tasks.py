"""Tasks module, specifying Hazen-related tasks and utilities."""

import importlib
import inspect
import sys
from importlib.metadata import version

from flask import current_app, jsonify, make_response

from app import db
from app.models import Report, Series
from hazen import worker


@worker.task(bind=True)
def produce_report(self, user_id, series_id, task_name, image_files, slice_width=None):
    # import Hazen functionality
    task_module = importlib.import_module(f"hazenlib.tasks.{task_name}")
    class_list = [cls for _, cls in inspect.getmembers(sys.modules[task_module.__name__], lambda x: inspect.isclass(x) and (x.__module__ == task_module.__name__))]
    if len(class_list) > 1:
        raise Exception(f'Task {task_module} has multiple class definitions: {class_list}')

    # Update Celery task status
    self.update_state(state='PENDING')

    # Pass image file path and variables to Hazenlib task
    task = getattr(task_module, class_list[0].__name__)(data_paths=image_files, report=True)
    # Perform task and generate result
    if task_name == 'snr':
        result_dict = task.run(slice_width)
    else:
        result_dict = task.run()
    for key, value in result_dict.items():
        # ignore reports section of the output
        if key == "reports":
            pass
        else:
            # reconstruct the measurement results
            result = {key: value}
    # Update Celery task status
    self.update_state(state='SUCCESS')

    # Store task result in the Report table
    report = Report(
        hazen_version=version('hazen'), data=result,
        user_id=user_id, series_id=series_id,
        task_name=task_name)  #  task_variable=task_variable
    # Save information to database
    report.save()
    
    # Update the has_report field of the corresponding Series
    series = Series.query.filter_by(id=series_id).first_or_404()
    series.update(has_report=True)
    # Commit all changes to the database
    db.session.commit()

    print("db updated")
    return result_dict
