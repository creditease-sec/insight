from flask import Blueprint

auth = Blueprint('auth', __name__, static_folder='../static')

from . import views