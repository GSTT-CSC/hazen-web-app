from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from alembic.config import Config

app = Flask(__name__)
app.config.from_pyfile('/Users/lce21/Documents/GitHub/hazen-web-app/config.py')

db = SQLAlchemy(app)
alembic_cfg = Config('/Users/lce21/Documents/GitHub/hazen-web-app/migrations/alembic.ini')
alembic_cfg.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])

with app.app_context():
    command = "revision"
    message = "Add docstring column to task table"
    alembic_args = [message]
    alembic_cfg.set_main_option('script_location', 'migrations')
    from alembic import command as alembic_command
    alembic_command.revision(alembic_cfg, command, *alembic_args)
