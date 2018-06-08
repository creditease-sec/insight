#-*- coding:utf-8 -*-
''' index 蓝本文件 '''

from flask import Blueprint


index = Blueprint('index', __name__, static_folder='../static')

from . import views
