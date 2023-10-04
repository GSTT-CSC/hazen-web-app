"""Tasks module, specifying Hazen-related tasks and utilities."""

import importlib
import inspect
import os
import sys
import shutil
from importlib.metadata import version

from flask import current_app, jsonify, make_response

from app import db
from app.models import Report, Series
from hazen import worker
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@worker.task(bind=True)
def produce_report(self, user_id, series_id, task_name, image_files, slice_width=None):
    logger.info("produce report")
    # import Hazen functionality
    task_module = importlib.import_module(f"hazenlib.tasks.{task_name}")
    logger.info(f"Performing {task_name} task on {series_id}")

    # Update Celery task status
    self.update_state(state='PENDING')

    # Pass image file path and variables to Hazenlib task
    try:
        task = getattr(task_module, task_name.capitalize())(
            input_data=image_files, report=True)  # , report_dir=report_dir
    except:
        class_list = [cls.__name__ for _, cls in inspect.getmembers(
            sys.modules[task_module.__name__],
            lambda x: inspect.isclass(x) and (x.__module__ == task_module.__name__)
            )]
        if len(class_list) == 1:
            task = getattr(task_module, class_list[0])(
            input_data=image_files, report=True)  # , report_dir=report_dir
            logger.info(task)
        else:
            raise Exception(
                f'Task {task_module} has multiple class definitions: {class_list}')

    # Perform task and generate result
    if task_name == 'snr':
        logger.info(f"running SNR task")
        result_dict = task.run(slice_width)
    else:
        logger.info(f"running task: {task}")
        result_dict = task.run()

    logger.info(result_dict)
    # measurement = json.dumps(result_dict['measurement'])

    # Update Celery task status
    self.update_state(state='SUCCESS')

    # Store task result in the Report table
    report = Report(
        hazen_version=version('hazen')[:10], data=result_dict['measurement'],
        user_id=user_id, series_id=series_id,
        task_name=task_name)  #  task_variable=task_variable
    # Save information to database
    report.save()

    basedir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(basedir, 'static',
                                report.filesystem_key) 
    os.makedirs(static_dir, exist_ok=True)
    directory = os.path.join(current_app.config['UPLOADED_PATH'],
                                report.filesystem_key)
    os.makedirs(directory, exist_ok=True)

    # Store report images in the appropriate folder under its report.id
    for file in result_dict['report_image']:
        logger.info(file)
        filename = os.path.basename(file)
        logger.info(filename)
        static_path = os.path.join(static_dir, filename)
        shutil.copy(file, static_path)
        print(f"file copied to {static_path}")
        permanent_path = os.path.join(directory, filename)
        shutil.move(file, permanent_path)

    # Update the has_report field of the corresponding Series
    series = Series.query.filter_by(id=series_id).first_or_404()
    series.update(has_report=True)
    # Commit all changes to the database
    db.session.commit()

    logger.info("db updated")
    return result_dict
