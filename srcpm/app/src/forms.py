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

# 实例化UploadSet类，创建一个图片set
# images = UploadSet('images', IMAGES)

''' 下拉选项 '''
action_choices = [('',''), (u'录入',u'录入'), (u'提交',u'提交')]
vul_type_level_choices = [('',''), (u'严重', u'严重'), (u'高危', u'高危'), (u'中危', u'中危'), (u'低危', u'低危')]
source_choices = [('',''), (u'安全部', u'安全部'), (u'YISRC', u'YISRC'), (u'公众平台', u'公众平台'), (u'合作伙伴', u'合作伙伴')]
vul_cata_choices = [('',''), (u'代码层面',u'代码层面'), (u'运维层面',u'运维层面')]


''' 漏洞报告提交表单 '''
class VulReportForm(Form):
	title = StringField(u'漏洞标题')
	related_asset = SelectField(u'关联资产')
	related_vul_cata = SelectField(u'漏洞层面', choices=vul_cata_choices)
	related_vul_type = SelectField(u'漏洞类型')
	vul_self_rank = SelectField('Rank', choices=[(str(n),n) for n in range(0,21)])
	vul_source = SelectField(u'漏洞来源', choices=source_choices)
	vul_poc = PageDownField(u'漏洞证明')
	vul_solution = PageDownField(u'解决方案')
	submit = SubmitField(u'提交')

	def __init__(self, *args, **kwargs):
		super(VulReportForm, self).__init__(*args, **kwargs)
		# 初始化表单时，从后台数据库读取域名列表供选择
		self.related_asset.choices = [('', '')] + [(ast.domain, ast.domain) for ast in Asset.query.all()]
		# 初始化表单时，从后台数据库读取漏洞类型列表供选择
		self.related_vul_type.choices = [('', '')] + [(vtp.vul_type, vtp.vul_type) for vtp in VulType.query.all()]


''' 漏洞报告管理修改提交表单 '''
class VulReportAdminForm(Form):
	title = StringField(u'漏洞标题')
	related_asset = StringField(u'关联资产')
	related_asset_inout = StringField(u'内外网')
	related_asset_status = StringField(u'资产状态')
	related_vul_cata = StringField(u'漏洞层面')
	related_vul_type = StringField(u'漏洞类型')
	vul_self_rank = StringField(u'自评Rank')
	vul_source = StringField(u'漏洞来源')
	vul_poc = PageDownField(u'漏洞证明')
	#vul_poc_html = StringField(u'漏洞证明HTML')
	vul_solution = PageDownField(u'解决方案')
	#vul_solution_html = StringField(u'解决方案HTML')
	grant_rank = StringField(u'Rank')
	vul_type_level = StringField(u'漏洞等级')
	risk_score = StringField(u'风险值')
	person_score = StringField(u'个人积分')
	done_solution = StringField(u'复测结果')
	done_rank = StringField(u'剩余Rank')
	residual_risk_score = StringField(u'剩余风险值')
	vul_status = StringField(u'漏洞状态')
	start_date = StringField(u'通告日期')
	end_date = StringField(u'结束日期')
	fix_date = StringField(u'修复日期')
	attack_check = StringField(u'攻击发现')
	submit = SubmitField(u'提交')


''' 上传图片提交表单 
class UploadImgForm(Form):
    upload = FileField(u'上传图片', validators=[
    								FileRequired(),
    								FileAllowed(['jpg', 'png'], 'Images only!')
    								]
    					)
    submit = SubmitField('Submit')
'''


''' 漏洞报告审核提交表单 '''
class VulReportReviewForm(Form):
	related_vul_cata = SelectField(u'漏洞层面', choices=vul_cata_choices)
	related_vul_type = SelectField(u'漏洞类型')
	grant_rank = SelectField(u'Rank', choices=[(str(n),n) for n in range(0,21)])
	start_date = DateField(u'通告日期')
	end_date = DateField(u'限定修复日期')
	submit = SubmitField(u'提交')

	def __init__(self, *args, **kwargs):
		super(VulReportReviewForm, self).__init__(*args, **kwargs)
		# 初始化表单时，从后台数据库读取漏洞类型列表供选择
		self.related_vul_type.choices = [('', '')] + [(vtp.vul_type, vtp.vul_type) for vtp in VulType.query.all()]


''' 漏洞报告申请复测提交表单 '''
class VulReportDevFinishForm(Form):
	dev_finish_solution = TextAreaField(u'修复方法')
	submit = SubmitField(u'提交')


''' 漏洞报告页面手动发送提醒邮件时，密码提交表单 '''
class VulReportSendEmailForm(Form):
	pwd = StringField(u'发送邮件密码')
	submit = SubmitField(u'提交')


''' 漏洞报告复测结果提交表单 '''
class VulReportRetestResultForm(Form):
	done_solution = TextAreaField(u'复测结果')
	done_rank = SelectField(u'剩余Rank', choices=[(str(n),n) for n in range(0,21)])
	end_date = DateField(u'限定修复日期')
	submit = SubmitField(u'提交')


''' 攻击发现结果提交表单 '''
class VulReportAttackForm(Form):
	attack_check = SelectField(u'攻击发现', choices=[('',''), (u'是',u'是'), (u'否',u'否')])
	submit = SubmitField(u'提交')


''' 漏洞层面提交表单 '''
class VulReportVulCataForm(Form):
	related_vul_cata = SelectField(u'漏洞层面', choices=vul_cata_choices)
	submit = SubmitField(u'提交')