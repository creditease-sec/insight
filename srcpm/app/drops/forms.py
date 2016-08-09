# -*- coding:utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
    SelectField, TextField, TextAreaField
from wtforms import ValidationError, TextField, DateField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask import request
from app.admin.models import Depart
from flask_pagedown.fields import PageDownField

# 搜索表单

class SearchForm(Form):
  search = StringField('search', validators = [Required(),Length(1, 20)])

# category表单


class CateForm(Form):
    catename = StringField(u'类别名', validators=[Required(),Length(1, 64)])
    submit = SubmitField(u'提交')
