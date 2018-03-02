#-*- coding:utf-8 -*-
''' drops 蓝本文件 '''

from flask import Blueprint


drops = Blueprint('drops', __name__, static_folder='../static')

from . import views
