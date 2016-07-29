#-*- coding:utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms import ValidationError, TextField, DateField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from ..admin.models import Asset, VulType
from flask import request
from app.admin.models import Depart
from flask_pagedown.fields import PageDownField



action_choices = [('',''), (u'录入',u'录入'), (u'提交',u'提交')]
vul_type_level_choices = [('',''), (u'严重', u'严重'), (u'高危', u'高危'), (u'中危', u'中危'), (u'低危', u'低危')]
source_choices = [('',''), (u'安全部', u'安全部'), (u'YISRC', u'YISRC'), (u'公众平台', u'公众平台'), (u'合作伙伴', u'合作伙伴')]




class VulRankForm(Form):
	date = DateField(u'日期')
	name = StringField(u'姓名')
	action = SelectField(u'事件分类', choices=action_choices)
	domain = SelectField(u'事件系统')
	vul_type = SelectField(u'漏洞类型')
	vul_type_level = SelectField(u'漏洞等级', choices=vul_type_level_choices)
	vul_id = StringField(u'漏洞ID')
	rank = IntegerField(u'Rank')
	source = SelectField(u'来源', choices=source_choices)
	score = IntegerField(u'积分')
	validate = BooleanField(u'是否有效')
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		super(VulRankForm, self).__init__(*args, **kwargs)
		self.domain.choices = [('', '')] + [(ast.domain, ast.domain) for ast in Asset.query.all()]
		self.vul_type.choices = [('', '')] + [(vtp.vul_type, vtp.vul_type) for vtp in VulType.query.all()]


class VulReportForm(Form):
	title = StringField(u'漏洞标题')
	related_asset = SelectField(u'关联资产')
	related_vul_type = SelectField(u'漏洞类型')
	vul_self_rank = IntegerField('Rank')
	vul_self_level = SelectField(u'漏洞等级', choices=vul_type_level_choices)
	vul_source = SelectField(u'漏洞来源', choices=source_choices)
	vul_poc = PageDownField(u'漏洞证明')
	vul_solution = PageDownField(u'解决方案')
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		super(VulReportForm, self).__init__(*args, **kwargs)
		self.related_asset.choices = [('', '')] + [(ast.domain, ast.domain) for ast in Asset.query.all()]
		self.related_vul_type.choices = [('', '')] + [(vtp.vul_type, vtp.vul_type) for vtp in VulType.query.all()]