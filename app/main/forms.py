from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length

from app.models import User


class AcquisitionForm(FlaskForm):
    acquisition = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
