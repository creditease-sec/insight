from flask import Blueprint


src = Blueprint('src', __name__)

from . import views