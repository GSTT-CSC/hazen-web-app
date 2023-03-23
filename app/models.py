"""
Sets databases to be created.
"""
import uuid

from sqlalchemy.dialects.postgresql import UUID

class SurrogatePK:
    """
    A mixin that adds a surrogate UUID primary key column 'id' to any
    declarative-mapped class.
    """

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

from app import db, login
from app.database import Model, SurrogatePK, CreatedTimestampMixin, JSONB
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from time import time
import jwt
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash


# to test - comment out lines 46 - 99 in __init__.py

@login.user_loader
def load_user(id):
    return User.query.get(str(id))


class User(UserMixin, Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "user"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    institution = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)  # why do we need index?
    email = db.Column(db.String(320), index=True, unique=True)  # why do we need index?
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-many bidirectional relationship
    # images = db.relationship('Image', back_populates='user')
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


class Image(Model, SurrogatePK, CreatedTimestampMixin):  # Previously "Acquisition"
    __tablename__ = "image"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    uid = db.Column(db.String(100))  # DICOM SOP Instance UID (0008,0018)
    filename = db.Column(db.String(200))
    header = db.Column(JSONB)  # DICOM Header
    series_id = db.Column(db.ForeignKey('series.id'))

    # Many-to-one relationships
    # user = db.relationship('User', back_populates='images')
    series = db.relationship('Series', back_populates='image')
    # studies = db.relationship('Study', back_populates='image')

    def __repr__(self):
        return '<Acquisition {}>'.format(self.description)

    @hybrid_property
    def filesystem_key(self):
        return self.id.hex


class Series(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "series"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    uid = db.Column(db.String(64))  # DICOM Series UID (0020,000E)
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
    reports = db.relationship('Report', back_populates='series', lazy='dynamic')

    # Many-to-one relationship # Child of
    user = db.relationship('User', back_populates='series')
    institutions = db.relationship('Institution', back_populates='series')
    devices = db.relationship('Device', back_populates='series')
    studies = db.relationship('Study', back_populates='series')

    @hybrid_property
    def filesystem_key(self):
        return self.id.hex


class Study(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "study"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    uid = db.Column(db.String(64))  # DICOM Study UID (0020,000D)
    description = db.Column(db.String(100))  # DICOM Study Description (0008,1030)

    # One-to-many relationships
    series = db.relationship('Series', back_populates='studies')


class Task(Model, SurrogatePK, CreatedTimestampMixin):  # Previously "ProcessTask"
    __tablename__ = "task"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    name = db.Column(db.String(100), unique=True)  # TODO: Change from reading hazenlib modules to classes

    # One-to-many relationship
    reports = db.relationship('Report', back_populates='task')


class Institution(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "institution"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    name = db.Column(db.String(100), unique=True)  # DICOM Institution (0008,0080)
    # series_id = db.Column(db.ForeignKey('series.id'))

    # One-to-many relationship
    series = db.relationship('Series', back_populates='institutions')


class Device(Model, SurrogatePK, CreatedTimestampMixin):
    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    manufacturer = db.Column(db.String(100))  # Device Manufacturer (0008,0070)
    station_name = db.Column(db.String(100))  # Station Name (0008, 1010)
    device_model = db.Column(db.String(100))  # Device Model (0008,1090)

    # One-to-many relationship
    series = db.relationship('Series', back_populates='devices')


class Report(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "report"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    hazen_version = db.Column(db.String(10))  # Hazenlib version
    data = db.Column(JSONB)  # Results

    user_id = db.Column(db.ForeignKey('user.id'))
    series_id = db.Column(db.ForeignKey('series.id'))
    task_name = db.Column(db.ForeignKey('task.name'))

    # Many-to-one relationships
    user = db.relationship('User', back_populates='reports')
    series = db.relationship('Series', back_populates='reports')
    task = db.relationship('Task', back_populates='reports')
