from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from app import db, login
from app.database import Model, SurrogatePK, CreatedTimestampMixin, JSONB
from flask import current_app
from flask_login import UserMixin
import uuid
from werkzeug.security import check_password_hash


@login.user_loader
def load_user(id):
    return User.query.get(str(id))

class User(UserMixin, Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "user"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    institution = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(320), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    series = db.relationship('Series', back_populates='user')
    reports = db.relationship('Report', back_populates='user')

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': str(self.id), 'exp': time() + expires_in},
            str(current_app.config['SECRET_KEY']), algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)





class Image(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "image"

    uid = db.Column(db.String(100))
    filename = db.Column(db.String(200))
    header = db.Column(JSONB)
    series_id = db.Column(db.ForeignKey('series.id'))

    series = db.relationship('Series', back_populates='image')

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    @hybrid_property
    def filesystem_key(self):
        return self.id.hex


class Series(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "series"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    uid = db.Column(UUID(as_uuid=True), default=uuid.uuid4)  # DICOM Series UID (0020,000E)
    description = db.Column(db.String(100))  # DICOM Series Description (0008,103E)
    series_datetime = db.Column(db.DateTime)  # DICOM Series Date and Series Time
    has_report = db.Column(db.Boolean, default=False)
    archived = db.Column(db.Boolean, default=False)

    """
    (0018, 1030) Protocol Name
    """
    user_id = db.Column(db.ForeignKey('user.id'))
    device_id = db.Column(db.ForeignKey('device.id'))
    institution_id = db.Column(db.ForeignKey('institution.id'))
    study_id = db.Column(db.ForeignKey('study.id'))

    # One-to-many relationships # Parent to
    image = db.relationship('Image', back_populates='series')
    reports = db.relationship('Report', back_populates='series')


    # Many-to-one relationship # Child of
    user = db.relationship('User', back_populates='series')
    institution = db.relationship('Institution', back_populates='series')
    device = db.relationship('Device', back_populates='series')
    study = db.relationship('Study', back_populates='series')



class Study(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "study"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uid = db.Column(db.String(64))  # DICOM Study UID (0020,000D)
    description = db.Column(db.String(100))  # DICOM Study Description (0008,1030)

    # One-to-many relationships
    series = db.relationship('Series', back_populates='study')


class Task(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "task"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), unique=True)  # TODO: Change from reading hazenlib modules to classes

    # One-to-many relationship
    reports = db.relationship('Report', back_populates='task')



class Institution(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "institution"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), unique=True)  # DICOM Institution (0008,0080)
    # series_id = db.Column(db.ForeignKey('series.id'))

    # One-to-many relationship
    series = db.relationship('Series', back_populates='institution')


class Device(Model, SurrogatePK, CreatedTimestampMixin):
    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manufacturer = db.Column(db.String(100))  # Device Manufacturer (0008,0070)
    station_name = db.Column(db.String(100))  # Station Name (0008, 1010)
    device_model = db.Column(db.String(100))  # Device Model (0008,1090)

    # One-to-many relationship
    series = db.relationship('Series', back_populates='device')


class Report(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "report"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hazen_version = db.Column(db.String(10))  # Hazenlib version
    data = db.Column(JSONB)  # Results

    user_id = db.Column(db.ForeignKey('user.id'))
    series_id = db.Column(db.ForeignKey('series.id'))
    task_id = db.Column(db.ForeignKey('task.id'))

    # Many-to-one relationships
    user = db.relationship('User', back_populates='reports')
    series = db.relationship('Series', back_populates='reports')
    task = db.relationship('Task', back_populates='reports')
