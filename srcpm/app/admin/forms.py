#-*- coding:utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, SelectField, ValidationError
from wtforms import DateField, TextField, IntegerField ,SubmitField
from wtforms.validators import Required, Length, Email
from flask import request
from .models import User, Depart, Role, Asset, VulType


perm_choices = [('admin.index', 'admin.index'),
				('admin.login_user_read', 'admin.login_user_read'),
				('admin.login_user_related', 'admin.login_user_related'),
				('admin.login_user_modify', 'admin.login_user_modify'),
				('admin.login_user_delete', 'admin.login_user_delete'),
				('admin.role_add', 'admin.role_add'),
				('admin.role_read', 'admin.role_read'),
				('admin.role_modify', 'admin.role_modify'),
				('admin.perm_modify', 'admin.perm_modify'),
				('admin.role_perm_delete', 'admin.role_perm_delete'),
				('src.vul_report_delete', 'src.vul_report_delete'),
				('src.vul_report_review','src.vul_report_review'),
				('src.vul_report_review_ajax','src.vul_report_review_ajax'),
				('src.vul_report_dev_finish','src.vul_report_dev_finish'),
				('src.vul_report_retest_result','src.vul_report_retest_result'),
				('src.vul_report_retest_ajax','src.vul_report_retest_ajax'),
				('src.vul_report_add','src.vul_report_add'),
				('src.upload_img','src.upload_img'),
				]


area_choices = [('',''), (u'外网', u'外网'), (u'内网', u'内网')]
status_choices = [('',''), (u'线上', u'线上'), (u'上线前', u'上线前')]
level_choices = [('',''), (u'一级', u'一级'), (u'二级', u'二级'), (u'三级', u'三级'), (u'其它', u'其它')]


class LoginForm(Form):
	email = StringField('Email', validators=[Required(), 
											Length(1, 64), Email()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')

class RoleForm(Form):
	role_name = StringField(u'角色名称', validators=[Required(),Length(1,64)])
	submit = SubmitField(u'提交')

class PermissionForm(Form):
	have_perm = SelectMultipleField(u'权限列表', choices=perm_choices)
	submit = SubmitField(u'提交')


class DepartForm(Form):
	department = StringField(u'部门', validators=[Required(), Length(1, 64)])
	leader = StringField(u'部门经理')
	email = StringField(u'邮件')
	submit = SubmitField('Submit')

	def validate_department(self, field):
		if request.endpoint[:19] != 'admin.depart_modify':
			if Depart.query.filter_by(department=field.data).first():
				raise ValidationError('Department already exist.')


class UserForm(Form):
	name = StringField(u'姓名', validators=[Required(), Length(1, 64)])
	email = StringField(u'邮件', validators=[Email()])
	department = SelectField(u'部门')
	submit = SubmitField('Submit')

	def validate_email(self, field):
		if request.endpoint[:17] != 'admin.user_modify':
			if User.query.filter_by(email=field.data).first():
				raise ValidationError('Email already exist.')

	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)
		self.department.choices = [('', '')] + [(dpt.department, dpt.department) for dpt in Depart.query.all()]


class UserRoleForm(Form):
	role_name = SelectField(u'角色')
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		super(UserRoleForm, self).__init__(*args, **kwargs)
		self.role_name.choices = [('', '')] + [(r.role_name, r.role_name) for r in Role.query.all()]



class AssetForm(Form):
	sysname = StringField(u'系统名称')
	domain = StringField(u'系统域名', validators=[Required(), Length(1, 64)])
	#root_dir = StringField(u'根目录')
	back_domain = TextField(u'备用域名')
	web_or_int = StringField(u'Web Or Interface')
	is_http = BooleanField('Is HTTP?')
	is_https = BooleanField('Is HTTPS?')
	in_or_out = SelectField(u'内外网', choices=area_choices)
	level = SelectField(u'重要等级', choices=level_choices)
	department = SelectField(u'部门')
	owner = StringField(u'负责人')
	status = SelectField(u'状态', choices=status_choices)
	#chkdate = DateField(u'检测日期')
	ps = TextField(u'说明')
	submit = SubmitField('Submit')

	def validate_domain(self, field):
		if request.endpoint[:19] != 'admin.assets_modify':
			if Asset.query.filter_by(domain=field.data).first():
				raise ValidationError('Domain already exist.')

	def __init__(self, *args, **kwargs):
		super(AssetForm, self).__init__(*args, **kwargs)
		self.department.choices = [('', '')] + [(dpt.department, dpt.department) for dpt in Depart.query.all()]


class VulTypeForm(Form):
	vul_type = StringField(u'漏洞类型')
	submit = SubmitField('Submit')

	def validate_domain(self, field):
		if request.endpoint[:18] != 'src.vul_type_modify':
			if VulType.query.filter_by(domain=field.data).first():
				raise ValidationError('Vul_type already exist.')


