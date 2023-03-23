import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    # other configuration variables...

class Config:
    CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    CELERY_RESULT_BACKEND = 'db+sqlite:///results.sqlite'


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hazen:Hazen!123@localhost/hazen'
