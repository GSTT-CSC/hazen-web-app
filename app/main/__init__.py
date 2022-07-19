from flask import Blueprint
from app.main import routes

bp = Blueprint('main', __name__, template_folder='templates')
