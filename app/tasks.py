"""Tasks module, specifying Hazen-related tasks and utilities."""

import importlib
import inspect
import sys
from importlib.metadata import version

from flask import current_app, jsonify, make_response

from app.models import Report, Series
from hazen import worker


@worker.task(bind=True)
def produce_report(self, user_id, series_id, task_name, image_files, slice_width):
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
        result = task.run(slice_width)
    else:
        result = task.run()
    print("result")
    print(result)
    for key,v in result.items():
        print(key)
        print(v)
        print(type(v))
        if type(v) != dict:
            result[key] = {}
            if type(v) == list:
                for i in range(len(v)):
                    result[key][f"position {i}"] = v[i]
            else:
                result[key]['measurement'] = v
    print(result)
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
    print("db updated")
    return result
