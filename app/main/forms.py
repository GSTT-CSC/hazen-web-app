from flask_wtf import FlaskForm
from wtforms import (
    MultipleFileField,
    SelectField,
    SelectMultipleField,
    RadioField,
    StringField,
    SubmitField,
)
from wtforms.validators import ValidationError, DataRequired, Length


# Upload files
class ImageUploadForm(FlaskForm):
    image_files = MultipleFileField()
    submit = SubmitField("Upload")


# Select task
class ProcessTaskForm(FlaskForm):
    task_name = SelectField("Process Task")
    task_variable = StringField("optional command arguments")
    submit = SubmitField("Run task")


# Select multiple Series and a Task
class BatchProcessingForm(FlaskForm):
    task_name = RadioField()
    many_series = SelectMultipleField()
    # task_variable = StringField(
    #     "optional command arguments", default="eg --measured_slice_width=3"
    # )
    submit = SubmitField("Run task on selected series")
