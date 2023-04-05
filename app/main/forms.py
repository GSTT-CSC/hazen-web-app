from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectField, SelectMultipleField, RadioField, StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length

from wtforms import FileField
from flask_wtf.file import FileRequired

from flask_wtf.file import FileRequired, FileAllowed

# Upload files
class ImageUploadForm(FlaskForm):
    image_files = MultipleFileField()
    folder_files = FileField("Choose Folder", render_kw={'webkitdirectory': True, 'multiple': True}, validators=[FileRequired()])
    submit = SubmitField('Upload')


# Upload folder
class FolderUploadForm(FlaskForm):
    folder = MultipleFileField(validators=[DataRequired()])
    submit = SubmitField('Upload')




# Select task
class ProcessTaskForm(FlaskForm):
    task_name = SelectField('Process Task')
    task_variable = StringField('Slice width for SNR measurement')
    submit = SubmitField('Run task')

# Select multiple Series and a Task
class BatchProcessingForm(FlaskForm):
    task_name = RadioField()
    many_series = SelectMultipleField()
    task_variable = StringField('Slice width for SNR measurement')
    submit = SubmitField('Run task on selected series')
