#-*- coding:utf-8 -*-
from flask import render_template
from . import main
import chartkick
from datetime import datetime

@main.route('/')
def index():
	data = {'hao': 150, 'jie': 200, 'yu': 100}
	return render_template('index.html', data=data)
