from flask import Blueprint


drops = Blueprint('drops', __name__, static_folder='../static')

from . import views
