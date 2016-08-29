from flask import Blueprint

main = Blueprint('main', __name__, static_folder='../static')

from . import views, errors

