from flask import Blueprint


src = Blueprint('src', __name__, static_folder='../static')

from . import views