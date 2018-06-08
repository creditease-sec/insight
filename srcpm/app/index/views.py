# -*- coding:utf-8 -*-

from flask import render_template, flash, url_for, redirect, request, current_app, session, jsonify, abort, make_response, send_file
from . import index 


@index.route('/')
def index():
    return redirect(url_for('main.index'))
