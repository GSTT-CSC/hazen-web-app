"""
Sets databases to be created.
"""

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
    username = db.Column(db.String(64), index=True, unique=True)  # why do we need index?
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    email = db.Column(db.String(320), index=True, unique=True)  # why do we need index?
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-many bidirectional relationship
    images = db.relationship('Image', back_populates='user')
    reports = db.relationship('Report', back_populates='user')

    @hybrid_property
    def filesystem_key(self):
        return self.id.hex

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
    uid = db.Column(db.String(64))  # DICOM UID
    filename = db.Column(db.String(200))
    user_id = db.Column(db.ForeignKey('user.id'))
    header = db.Column(JSONB)  # DICOM Header

    user = db.relationship('User', back_populates='images')

    # Many-to-one relationships
    series = db.relationship('Series', back_populates='image')
    studies = db.relationship('Study', back_populates='image')

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
    image_id = db.Column(db.ForeignKey('image.id'))
    uid = db.Column(db.String(64))  # DICOM Series UID (0020,000E)
    description = db.Column(db.String(100))  # DICOM Series Description (0008,103E)

    # One-to-many relationships
    image = db.relationship('Image', back_populates='series')
    reports = db.relationship('Report', back_populates='series', lazy='dynamic')

    # Many-to-one relationship
    institutions = db.relationship('Institution', back_populates='series')
    devices = db.relationship('Device', back_populates='series')


class Study(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "study"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    image_id = db.Column(db.ForeignKey('image.id'))
    uid = db.Column(db.String(64))  # DICOM Study UID (0020,000D)
    description = db.Column(db.String(100))  # DICOM Study Description (0008,1030)

    # One-to-many relationships
    image = db.relationship('Image', back_populates='studies')


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
    series_id = db.Column(db.ForeignKey('series.id'))
    name = db.Column(db.String(100), unique=True)  # DICOM Institution (0008,0080)

    # One-to-many relationship
    series = db.relationship('Series', back_populates='institutions')


class Device(Model, SurrogatePK, CreatedTimestampMixin):
    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    series_id = db.Column(db.ForeignKey('series.id'))
    manufacturer = db.Column(db.String(100))  # Device Manufacturer (0008,0070)
    device = db.Column(db.String(100))  # Device Model (0008,1090)

    # One-to-many relationship
    series = db.relationship('Series', back_populates='devices')


class Report(Model, SurrogatePK, CreatedTimestampMixin):
    __tablename__ = "report"

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    # Column "id" is created automatically by SurrogatePK() from database.py
    user_id = db.Column(db.ForeignKey('user.id'))
    series_id = db.Column(db.ForeignKey('series.id'))
    task_name = db.Column(db.ForeignKey('task.name'))
    data = db.Column(JSONB)  # Results
    hazen_version = db.Column(db.String(10))  # Hazenlib version

    # Many-to-one relationships
    user = db.relationship('User', back_populates='reports')
    series = db.relationship('Series', back_populates='reports')
    task = db.relationship('Task', back_populates='reports')

