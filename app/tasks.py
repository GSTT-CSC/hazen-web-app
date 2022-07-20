"""Tasks module, specifying Hazen-related tasks and utilities."""

import os
import pydicom

from flask import current_app, flash, jsonify

from app.models import ProcessTask, Fact

from hazen import worker


@worker.task(bind=True)
def produce_report(self, function_name, acquisition):
    # import Hazen functionality
    task = __import__(f'hazenlib.{function_name}', globals(), locals(), [f'{function_name}'])
    current_app.logger.info(f"Producing report from {task.__name__}")
    process = ProcessTask.query.filter_by(name=function_name).first()

    # Select files to perform task on
    filesystem_folder = os.path.join(current_app.config['UPLOADED_PATH'],
                                    acquisition['author_hex'],
                                    acquisition['hex'])
    image_files = [os.path.join(filesystem_folder, file) for file in os.listdir(filesystem_folder)]
    # Load images into DICOM dataset
    dcms = [pydicom.read_file(x, force=True) for x in image_files]

    # Ensure that appropriate number of files were selected
    if len(dcms) != acquisition['files']:
        raise Exception('Number of dicoms in directory not equal to expected!')

    # Perform analysis/task
    self.update_state(state='IN PROGRESS')
    self.acquisition_id = acquisition['hex']
    # Perform task and generate result
    result = task.main(data=dcms)
    self.update_state(state='STORING RESULTS')
    # Store analysis result in database
    fact = Fact(user_id=acquisition['author_id'],
                acquisition_id=acquisition['id'],
                process_task=process.id,
                process_task_variables={},
                data=result,
                status='Complete')
    # Save information to database
    fact.save()
    flash(f'Completed process: {function_name}')
    return jsonify(fact.data)
