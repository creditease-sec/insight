#-*- coding:utf-8 -*-

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms import ValidationError, TextField, DateField, IntegerField,TextAreaField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from ..admin.models import Asset, VulType
from flask import request
from app.admin.models import Depart
from flask_pagedown.fields import PageDownField


images = UploadSet('images', IMAGES)

action_choices = [('',''), (u'录入',u'录入'), (u'提交',u'提交')]
vul_type_level_choices = [('',''), (u'严重', u'严重'), (u'高危', u'高危'), (u'中危', u'中危'), (u'低危', u'低危')]
source_choices = [('',''), (u'安全部', u'安全部'), (u'YISRC', u'YISRC'), (u'公众平台', u'公众平台'), (u'合作伙伴', u'合作伙伴')]



class VulReportForm(Form):
	title = StringField(u'漏洞标题')
	related_asset = SelectField(u'关联资产')
	related_vul_type = SelectField(u'漏洞类型')
	vul_self_rank = SelectField('Rank', choices=[(str(n),n) for n in range(0,21)])
	vul_source = SelectField(u'漏洞来源', choices=source_choices)
	vul_poc = PageDownField(u'漏洞证明')
	vul_solution = PageDownField(u'解决方案')
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		super(VulReportForm, self).__init__(*args, **kwargs)
		self.related_asset.choices = [('', '')] + [(ast.domain, ast.domain) for ast in Asset.query.all()]
		self.related_vul_type.choices = [('', '')] + [(vtp.vul_type, vtp.vul_type) for vtp in VulType.query.all()]



class UploadImgForm(Form):
    upload = FileField(u'上传图片', validators=[
    								FileRequired(),
    								FileAllowed(['jpg', 'png'], 'Images only!')
    								]
    					)
    submit = SubmitField('Submit')

class VulReportReviewForm(Form):
	related_vul_type = SelectField(u'漏洞类型')
	grant_rank = SelectField(u'Rank', choices=[(str(n),n) for n in range(0,21)])
	start_date = DateField(u'通告日期')
	end_date = DateField(u'限定修复日期')
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		super(VulReportReviewForm, self).__init__(*args, **kwargs)
		self.related_vul_type.choices = [('', '')] + [(vtp.vul_type, vtp.vul_type) for vtp in VulType.query.all()]

class VulReportDevFinishForm(Form):
	dev_finish_solution = TextAreaField(u'修复方法')
	submit = SubmitField('Submit')

class VulReportRetestResultForm(Form):
	done_solution = TextAreaField(u'复测结果')
	done_rank = SelectField(u'剩余Rank', choices=[(str(n),n) for n in range(0,21)])
	end_date = DateField(u'限定修复日期')
	submit = SubmitField('Submit')