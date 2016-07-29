#-*- coding:utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, ValidationError, TextField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask import request
from models import Depart, User




class DepartForm(Form):
	department = StringField(u'部门', validators=[Required(), Length(1, 64)])
	leader = StringField(u'部门经理')
	email = StringField(u'邮件')
	submit = SubmitField('Submit')

	def validate_department(self, field):
		if request.endpoint[:19] != 'user.departs_modify':
			if Depart.query.filter_by(department=field.data).first():
				raise ValidationError('Department already exist.')


class UserForm(Form):
	name = StringField(u'姓名', validators=[Required(), Length(1, 64)])
	email = StringField(u'邮件', validators=[Email()])
	department = SelectField(u'部门')
	submit = SubmitField('Submit')

	def validate_email(self, field):
		if request.endpoint[:17] != 'user.users_modify':
			if User.query.filter_by(email=field.data).first():
				raise ValidationError('Email already exist.')

	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)
		self.department.choices = [('', '')] + [(dpt.department, dpt.department) for dpt in Depart.query.all()]