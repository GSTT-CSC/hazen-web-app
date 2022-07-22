from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, MultipleFileField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length

# Upload files form
class ImageUploadForm(FlaskForm):
    images = MultipleFileField()
    submit = SubmitField('Submit')


# Select task form
class ProcessTaskForm(FlaskForm):
    task_name = SelectField('Process Task')
    task_variable = StringField('Slice width for SNR measurement')
    submit = SubmitField('Run task')
