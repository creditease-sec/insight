from flask import Blueprint


drops = Blueprint('drops', __name__)

from . import views
