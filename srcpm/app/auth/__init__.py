#-*- coding:utf-8 -*-
''' auth 蓝本文件 '''

from flask import Blueprint

auth = Blueprint('auth', __name__, static_folder='../static')

from . import views