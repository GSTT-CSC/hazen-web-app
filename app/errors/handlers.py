from flask import render_template

from app.errors import bp
from app import db


@bp.app_errorhandler(404)
def not_found_error(error):
    """
    Throws an error when the page cannot be found.
    """
    return render_template('404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    """
    Throws an internal server error.
    """
    db.session.rollback()
    return render_template('500.html'), 500
