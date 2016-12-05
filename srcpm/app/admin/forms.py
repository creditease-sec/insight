#-*- coding:utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, SelectField, ValidationError
from wtforms import DateField, TextField, IntegerField ,SubmitField, TextAreaField
from wtforms.validators import Required, Length, Email
from flask import request
from .models import User, Depart, Role, Asset, VulType


perm_choices = [('admin.index',u'管理后台－首页'),        #管理后台－首页
				('admin.login_user_read', u'管理后台－用户查看'),        #管理后台－用户查看
				('admin.login_user_related', u'管理后台－用户关联'),        #管理后台－用户关联
				('admin.login_user_modify', u'管理后台－用户修改'),        #管理后台－用户修改
				('admin.login_user_delete', u'管理后台－用户删除'),        #管理后台－用户删除
				('admin.role_add', u'管理后台－角色增加'),        #管理后台－角色增加
				('admin.role_read', u'管理后台－角色读取'),        #管理后台－角色读取
				('admin.role_modify', u'管理后台－角色修改'),        #管理后台－角色修改
				('admin.perm_modify', u'管理后台－权限修改'),        #管理后台－权限修改
				('admin.role_perm_delete', u'管理后台－角色权限删除'),        #管理后台－角色权限删除
				('admin.depart_add',u'管理后台－部门增加'),        #管理后台－部门增加
				('admin.depart_read',u'管理后台－部门查看'),        #管理后台－部门查看
				('admin.depart_modify',u'管理后台－部门修改'),        #管理后台－部门修改
				('admin.depart_delete',u'管理后台－部门删除'),        #管理后台－部门删除
				('admin.user_add',u'管理后台－员工增加'),        #管理后台－员工增加
				('admin.user_read',u'管理后台－员工查看'),        #管理后台－员工查看
				('admin.user_modify',u'管理后台－员工修改'),        #管理后台－员工修改
				('admin.user_delete',u'管理后台－员工删除'),        #管理后台－员工删除
				('admin.assets_add',u'管理后台－资产增加'),        #管理后台－资产增加
				('admin.assets_add_ajax',u'管理后台－资产增加AJAX'),        #管理后台－资产增加AJAX
				('admin.assets_read',u'管理后台－资产查看'),        #管理后台－资产查看
				('admin.assets_modify',u'管理后台－资产修改'),        #管理后台－资产修改
				('admin.assets_delete',u'管理后台－资产删除'),        #管理后台－资产删除
				('admin.vul_type_add',u'管理后台－漏洞类型增加'),        #管理后台－漏洞类型增加
				('admin.vul_type_read',u'管理后台－漏洞类型查看'),        #管理后台－漏洞类型查看
				('admin.vul_type_modify',u'管理后台－漏洞类型修改'),        #管理后台－漏洞类型修改
				('admin.vul_type_delete',u'管理后台－漏洞类型删除'),        #管理后台－漏洞类型删除
				('src.vul_report_delete', u'SRC－漏洞报告删除'),        #SRC－漏洞报告删除
				('src.vul_report_admin_edit', u'SRC－漏洞报告管理编辑'),        #SRC－漏洞报告管理编辑
				('src.vul_report_review',u'SRC-漏洞报告审核'),        #SRC-漏洞报告审核
				('src.vul_report_review_ajax',u'SRC-漏洞报告审核AJAX'),        #SRC-漏洞报告审核AJAX
				('src.vul_report_send_email', u'SRC-漏洞报告发送邮件'),		#SRC-漏洞报告发送邮件
				('src.vul_report_known',u'SRC-漏洞报告－已知悉提交'),        #SRC-漏洞报告－已知悉提交
				('src.vul_report_dev_finish',u'SRC-漏洞报告－申请复测'),        #SRC-漏洞报告－申请复测
				('src.vul_report_retest_result',u'SRC-漏洞报告－复测结果提交'),        #SRC-漏洞报告－复测结果提交
				('src.vul_report_retest_ajax',u'SRC-漏洞报告－复测结果提交AJAX'),        #SRC-漏洞报告－复测结果提交AJAX
				('src.vul_report_add',u'SRC-漏洞报告-增加'),      #SRC-漏洞报告-增加
				('src.upload_img',u'SRC-漏洞报告－上传'),        #SRC-漏洞报告－上传
				('src.vul_review_list',u'SRC-漏洞报告－未审核列表'),        #SRC-漏洞报告－未审核列表
				('src.assets_read',u'SRC-资产查看'),        #SRC-资产查看
				('src.assets_add',u'SRC-资产增加'),        #SRC-资产增加
				('src.assets_add_ajax',u'SRC－资产增加AJAX'),        #SRC-资产增加AJAX
				('src.assets_modify',u'SRC-资产修改'),        #SRC-资产修改
				('main.index_count',u'MAIN-漏洞报告统计'),		#MAIN-漏洞报告统计
                ('drops.manager',u'SRC－知识库管理'),        #SRC－知识库管理
				]


area_choices = [('',''), (u'外网', u'外网'), (u'内网', u'内网')]
status_choices = [('',''), (u'线上', u'线上'), (u'上线前', u'上线前'),(u'下线', u'下线')]
level_choices = [('',''), (u'一级', u'一级'), (u'二级', u'二级'), (u'三级', u'三级'), (u'其它', u'其它')]
secure_level_choices = [('',''), (u'安全一级', u'安全一级'), (u'安全二级', u'安全二级'), (u'安全三级', u'安全三级'), (u'安全其它', u'安全其它')]
count_private_data_choice = [('',''), (u'几十条', u'几十条'), (u'几百条', u'几百条'), (u'几千条', u'几千条'), (u'几万条及以上', u'几万条及以上')]
down_time_choice = [('',''), (u'几分钟', u'几分钟'), (u'几十分钟', u'几十分钟'), (u'几小时', u'几小时'), (u'几天', u'几天')]

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
	submit = SubmitField(u'提交')

	def validate_department(self, field):
		if request.endpoint[:19] != 'admin.depart_modify':
			if Depart.query.filter_by(department=field.data).first():
				raise ValidationError(u'部门已经存在')


class UserForm(Form):
	name = StringField(u'姓名', validators=[Required(), Length(1, 64)])
	email = StringField(u'邮件', validators=[Email()])
	department = SelectField(u'部门')
	submit = SubmitField(u'提交')

	def validate_email(self, field):
		if request.endpoint[:17] != 'admin.user_modify':
			if User.query.filter_by(email=field.data).first():
				raise ValidationError(u'邮箱已经存在')

	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)
		self.department.choices = [('', '')] + [(dpt.department, dpt.department) for dpt in Depart.query.all()]


class UserRoleForm(Form):
	role_name = SelectField(u'角色')
	submit = SubmitField(u'提交')

	def __init__(self, *args, **kwargs):
		super(UserRoleForm, self).__init__(*args, **kwargs)
		self.role_name.choices = [('', '')] + [(r.role_name, r.role_name) for r in Role.query.all()]



class AssetForm(Form):
	sysname = StringField(u'系统名称')
	domain = StringField(u'系统域名', validators=[Required(), Length(1, 64)])
	back_domain = TextField(u'备用域名')
	web_or_int = StringField(u'Web Or Interface')
	is_http = BooleanField('Is HTTP?')
	is_https = BooleanField('Is HTTPS?')
	in_or_out = SelectField(u'内外网', choices=area_choices)
	level = SelectField(u'重要等级', choices=level_choices)
	department = SelectField(u'部门')
	owner = StringField(u'负责人')
	status = SelectField(u'状态', choices=status_choices)
	private_data = TextAreaField(u'敏感数据说明')
	count_private_data = SelectField(u'敏感数据条数', choices=count_private_data_choice)
	down_time = SelectField(u'允许宕机时长', choices=down_time_choice)
	secure_level = SelectField(u'安全重要等级', choices=secure_level_choices)
	ps = TextField(u'说明')
	submit = SubmitField(u'提交')

	def validate_domain(self, field):
		if (request.endpoint[:19] != 'admin.assets_modify') and (request.endpoint[:17] != 'src.assets_modify'):
			if Asset.query.filter_by(domain=field.data).first():
				raise ValidationError(u'域名已经存在')

	def __init__(self, *args, **kwargs):
		super(AssetForm, self).__init__(*args, **kwargs)
		self.department.choices = [('', '')] + [(dpt.department, dpt.department) for dpt in Depart.query.all()]
		#self.owner.choices = [('', '')] + [(user.email, user.name) for user in User.query.filter_by(department=u'信息系统安全部')]

class VulTypeForm(Form):
	vul_type = StringField(u'漏洞类型')
	submit = SubmitField(u'提交')

	def validate_domain(self, field):
		if request.endpoint[:18] != 'src.vul_type_modify':
			if VulType.query.filter_by(domain=field.data).first():
				raise ValidationError(u'漏洞类型已经存在')
