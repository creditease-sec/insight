#-*- coding:utf-8 -*-
''' src 蓝本文件 '''

from flask import Blueprint


src = Blueprint('src', __name__, static_folder='../static')

from . import views