from flask import Blueprint

admin = Blueprint('admin', __name__, static_folder='../static')

from . import views