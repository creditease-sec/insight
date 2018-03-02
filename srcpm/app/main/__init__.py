#-*- coding:utf-8 -*-
''' main 蓝本文件 '''

from flask import Blueprint

main = Blueprint('main', __name__, static_folder='../static')

from . import views, errors

