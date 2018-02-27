#-*- coding:utf-8 -*-
''' admin 蓝本文件 '''

from flask import Blueprint

admin = Blueprint('admin', __name__, static_folder='../static')

from . import views