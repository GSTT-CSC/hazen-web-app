"""Main script to set up the web app

"""
# Import necessary packages, modules and scripts
import os
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler

from config import Config

from flask import Flask, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_mail import Mail
from flask_moment import Moment
from flask_dropzone import Dropzone
from flask_heroku import Heroku
from celery import Celery


# Alias common variables
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
bootstrap = Bootstrap5()
moment = Moment()
dropzone = Dropzone()
heroku = Heroku()


# Set up a Flask app
def create_app(config_class=Config):
    app = Flask(__name__)
    # with information specified in the config.py
    app.config.from_object(config_class)
    # connect to the database
    db.init_app(app)
    migrate.init_app(app, db)
    db.create_all(app=app)
    # Initialise additional functionality
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    dropzone.init_app(app)
    heroku.init_app(app)

    # Add project-specific functionality
    # Main page - Dashboard
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    # Upload directory to hold files
    os.makedirs(app.config['UPLOADED_PATH'], exist_ok=True)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    # Authentication pages to login, logout, change password
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Actions in production mode
    if not app.debug:
        # Set up the mail server
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # Set up logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/hazen.log', maxBytes=10240,
                                            backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Hazen startup')

    return app


def create_celery_app(app=None):
    app = app or create_app()
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'], include=['app.tasks'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
