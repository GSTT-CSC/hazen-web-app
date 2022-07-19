from flask import Blueprint
from app.uploader import routes

bp = Blueprint('uploader', __name__, template_folder='templates')
