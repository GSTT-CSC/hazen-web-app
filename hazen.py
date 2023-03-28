import os
import pkgutil
import importlib

from flask import current_app

from app import db, create_app, create_celery_app
from app.models import User, Image, Series, Study, Device, Institution, Task, Report

__version__ = '0.1.dev0'
__author__ = "mohammad_haris.shuaib@kcl.ac.uk"


def register_tasks_in_db():
    from hazenlib import tasks as hazen_tasks
    # TODO: Change to read from hazenlib classes
    tasks = {f'{modname}': importlib.import_module(
        f'hazenlib.tasks.{modname}') for importer, modname, ispkg in
        pkgutil.iter_modules(hazen_tasks.__path__)}

    with app.app_context():
        stored_tasks = Task.query.all()

        for stored_task in stored_tasks:
            if stored_task.name in tasks.keys():
                _ = tasks.pop(stored_task.name)
                current_app.logger.info(f'{stored_task.name} already exists in db')

        for name, obj in tasks.items():
            tasks = Task(name=name)
            tasks.save()


app = create_app()
app.secret_key = app.config['SECRET_KEY']
worker = create_celery_app(app)  # a Celery object
register_tasks_in_db()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Institution': Institution,
            'Image': Image, 'Series': Series, 'Study': Study, 'Device': Device,
            'Task': Task, 'Report': Report}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5001)), debug=True, use_reloader=True)
