import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    # Check if on Heroku or running locally
    platform = 'local'
    if 'REDIS_URL' in os.environ:
        platform = 'heroku'
    elif 'RUNNING_ON_DOCKER' in os.environ:
        platform = 'docker'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    if platform == 'heroku':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("://", "ql://", 1) or 'postgresql://localhost:5432/hazen'

    elif platform == 'docker':

        pg_db = os.environ.get('POSTGRES_DB')
        pg_user = os.environ.get('POSTGRES_USER')
        pg_pw = os.environ.get('POSTGRES_PASSWORD')

        SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{pg_user}:{pg_pw}@hazen_db:5432/{pg_db}'

    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost:5432/hazen'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [os.environ.get('ADMIN_EMAIL')] or ['haris.shuaib@gmail.com']

    ACQUISITIONS_PER_PAGE = 9

    LANGUAGES = ['en-GB', 'fr']

    UPLOADED_PATH = os.path.join(basedir, 'uploads')
    DROPZONE_MAX_FILE_SIZE = 3
    DROPZONE_MAX_FILES = 20
    DROPZONE_UPLOAD_ON_CLICK = True
    DROPZONE_ALLOWED_FILE_TYPE = 'application/dicom, .IMA'
    DROPZONE_ALLOWED_FILE_CUSTOM = True

    if platform == 'heroku':
        CELERY_BROKER_URL = os.environ.get('REDIS_URL')  # for Redis
        CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')  # for Redis

    elif platform == 'docker':
        CELERY_BROKER_URL = 'redis://redis:6379/0'  # for Redis
        CELERY_RESULT_BACKEND = 'redis://redis:6379/0'  # for Redis

    else:
        CELERY_BROKER_URL = 'amqp://localhost'  # for RabbitMQ
        CELERY_RESULT_BACKEND = 'rpc://'  # for RabbitMQ
