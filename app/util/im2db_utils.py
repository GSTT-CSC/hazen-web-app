import os
import shutil
import pydicom
import datetime

from app import db
from app.models import Image, Series, Study, Device, Task, Report
from flask_login import current_user
from flask import current_app, flash, url_for, redirect
from werkzeug.utils import secure_filename


class ImageExistsError(Exception): pass


def upload_file(file):
    filename = secure_filename(file.filename)
    secure_path = os.path.join(current_app.config['UPLOADED_PATH'], filename)
    try:
        file.save(secure_path)
    except IsADirectoryError:
        flash("No files were selected", 'info')
        return redirect(url_for('main.workbench'))

    try:
        filesystem_dir = ingest_image(secure_path)
        permanent_path = os.path.join(filesystem_dir, filename)
        shutil.move(secure_path, permanent_path)
        flash(f'{filename} file has been uploaded successfully!', 'success')
    except ImageExistsError:
        os.remove(secure_path)
        flash(f'{filename} file has already been uploaded!', 'danger')


# Upload images one at a time and parse metadata from DICOM header
def ingest_image(file_path):
    try:
        # Load in the DICOM header into a pydicom Dataset
        dcm = pydicom.read_file(file_path, force=True,
                                                stop_before_pixels=True)

        # Parse the relevant fields into variables
        image_uid = dcm.SOPInstanceUID
        # Ensure that image is not yet in database
        image_exists = db.session.query(db.exists().where(Image.uid == image_uid)).scalar()
        if image_exists:
            current_app.logger.info('Image already exists in database')
            raise ImageExistsError(f"UID: {image_uid}")

        # Collect relevant pieces of information from DICOM header
        series_uid = dcm.SeriesInstanceUID
        study_uid = dcm.StudyInstanceUID
        description = f"{dcm.StudyDescription}: {dcm.SeriesDescription}"
        filename = os.path.basename(file_path)

        # 0020 Study date
        study_date = dcm.StudyDate
        # 0030 study time
        study_time = dcm.StudyTime
        institution = dcm.InstitutionName
        # 0070 manufacturer
        manufacturer = dcm.Manufacturer
        # (0008,1090)	LO	Manufacturer's Model Name
        model = dcm[0x00081090].value
        station_name = dcm.StationName
        # 0050 accession number
        accession_number = dcm.AccessionNumber
        # print({"institution": institution,
        #        "manufacturer": manufacturer,
        #        "model": model,
        #        "study_date": study_date,
        #        "study_time": study_time,
        #        "station_name": station_name,
        #        "accession_number": accession_number
        #        })

        # Save the image data into the corresponding tables:
        # 0. Device:
        try:
            device_id = Device.query.where(Device.institution == institution
                ).where(Device.manufacturer == manufacturer
                ).where(Device.device_model == model
                ).where(Device.station_name == station_name).first().id
        except:
            new_device = Device(
                institution=institution, manufacturer=manufacturer,
                device_model=model, station_name=station_name)
            new_device.save()
            device_id = new_device.id
        #TODO remove in production
        print("device id:", device_id)
        
        # 1. Study:
        try:
            study_id = Study.query.filter_by(uid=study_uid).first().id
        except:
            new_study = Study(uid=study_uid,
                              description=dcm.StudyDescription,
                              study_date=study_date)
            new_study.save()
            study_id = new_study.id
        #TODO remove in production
        print("study id:", study_id)
        
        # 2. Series:
        try:
            series_id = Series.query.filter_by(uid=series_uid).first().id
        except:
            series_datetime = datetime.strptime("-".join(
                                [dcm.SeriesDate, dcm.SeriesTime.split('.')[0]]
                                    ), '%Y%m%d-%H%M%S')

            new_series = Series(
                uid=series_uid, description=dcm.SeriesDescription, user_id=current_user.get_id(), device_id=device_id,
                study_id=study_id, series_datetime=series_datetime)
            new_series.save()
            series_id = new_series.id
        #TODO remove in production
        print("series id:", series_id)

        # 3. Image:
        new_image = Image(
            uid=image_uid, series_id=series_id, filename=filename,
            accession_number=accession_number)
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


def locate_image_files(filesystem_key, filename=False):
    # Select files in series folder
    folder = os.path.join(current_app.config['UPLOADED_PATH'],
                                    filesystem_key)
    if filename == True:
        image_files = os.listdir(folder)
    else:
        image_files = [os.path.join(folder, file) for file in os.listdir(folder)]
    
    return image_files


def delete_series(series_id):
    pass