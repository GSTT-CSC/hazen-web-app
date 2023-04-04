import os
import pkgutil
import importlib

from flask import current_app

from app import db, create_app, create_celery_app
from app.models import User, Image, Series, Study, Device, Institution, Task, Report

__version__ = '0.1.dev0'
__author__ = "mohammad_haris.shuaib@kcl.ac.uk"


import os
import inspect

import os
import inspect
import ast


def register_tasks_in_db():
    from hazenlib import tasks as hazen_tasks
    tasks = {
        f'{modname}': importlib.import_module(f'hazenlib.tasks.{modname}')
        for importer, modname, ispkg in pkgutil.iter_modules(hazen_tasks.__path__)
    }

    def get_module_docstring(filepath):
        with open(filepath, 'r') as f:
            content = f.read()

        parsed_module = ast.parse(content)
        for node in parsed_module.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                return inspect.cleandoc(node.value.s)
        return ''

    with app.app_context():
        stored_tasks = Task.query.all()

        for stored_task in stored_tasks:
            if stored_task.name in tasks.keys():
                module_file = os.path.join(os.path.dirname(hazen_tasks.__file__), f"{stored_task.name}.py")
                docstring = get_module_docstring(module_file)

                # Update the task's docstring
                stored_task.docstring = docstring

                # Commit the changes to the database
                db.session.commit()

                print(f"Updated task {stored_task.name} with docstring:\n{docstring}\n")
                _ = tasks.pop(stored_task.name)
                current_app.logger.info(f'{stored_task.name} already exists in db')

        if tasks:
            current_app.logger.warning(f"The following tasks were not found in the database: {', '.join(tasks.keys())}")


app = create_app()
app.secret_key = app.config['SECRET_KEY']
worker = create_celery_app(app)  # a Celery object
register_tasks_in_db()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Institution': Institution,
            'Image': Image, 'Series': Series, 'Study': Study, 'Device': Device,
            'Task': Task, 'Report': Report, 'doc': doc}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5001)))
