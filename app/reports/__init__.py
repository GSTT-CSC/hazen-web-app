from flask import Blueprint
from app.reports import routes

bp = Blueprint('reports', __name__, template_folder='templates')
