#-*- coding:utf-8 -*-

from flask import render_template, flash, url_for, redirect, request, current_app, session, jsonify, abort
from . import src
from .forms import VulReportForm, UploadImgForm, VulReportReviewForm
from .forms import VulReportDevFinishForm, VulReportRetestResultForm
from .models import VulReport, VulLog
from ..admin.models import Asset, User, Depart
from .. import db
import datetime
from flask_login import current_user, login_required
from werkzeug import secure_filename
from ..email import send_email
from ..decorators import permission_required



#-------------漏洞报告模块------------------------------------------------------------------------------

@src.route('/vul_report_add', methods=['GET', 'POST'])
@login_required
@permission_required('src.vul_report_add')
def vul_report_add():
	form = VulReportForm()
	if form.validate_on_submit():
		#获取关联资产的内外网、状态信息
		asset_get = Asset.query.filter_by(domain=form.related_asset.data).first()
		if asset_get is None:
			return abort(500)

		vul_rpt = VulReport(author=current_user.related_name, 
					title = form.title.data,
					related_asset = form.related_asset.data,
					related_asset_inout = asset_get.in_or_out,
					related_asset_status = asset_get.status,
					related_vul_type = form.related_vul_type.data,
					vul_self_rank = form.vul_self_rank.data,
					vul_source = form.vul_source.data,
					vul_poc = form.vul_poc.data,
					vul_solution  = form.vul_solution.data,
					)
		db.session.add(vul_rpt)
		flash('Vul_report %s-%s add success!' %(current_user.related_name, form.title.data))
		return redirect(url_for('src.vul_report_list_read'))
	return render_template('src/vul_report_add.html', form=form)

#-----------------------上传图片----------------------------------------------------------

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@src.route('/upload_img', methods=['POST'])
@permission_required('src.upload_img')
def upload_img():
	up_img_file = request.files['upload']
	if up_img_file and allowed_file(up_img_file.filename):
		img_type = up_img_file.filename.rsplit('.', 1)[1]
		save_filename = datetime.datetime.now().strftime('%Y%m%d%H%M%s') + '.' + img_type
		up_img_file.save(current_app.config['UPLOAD_IMG_FOLDER'] + save_filename)
		session['filename'] = url_for('static', filename='upload/img/'+save_filename)
		return jsonify(result=session['filename'])


@src.route('/vul_report_list_read', methods=['GET', 'POST'])
def vul_report_list_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		vul_report_list_result = VulReport.query.all()
	else:
		vul_report_list_result = VulReport.query.filter(VulReport.author.like("%" + opt + "%")
											| VulReport.timestamp.like("%" + opt + "%")
											| VulReport.title.like("%" + opt + "%")
											| VulReport.related_asset.like("%" + opt + "%")
											| VulReport.related_asset_inout.like("%" + opt + "%")
											| VulReport.related_asset_status.like("%" + opt + "%")
											| VulReport.related_vul_type.like("%" + opt + "%")
											| VulReport.vul_self_level.like("%" + opt + "%")
											| VulReport.vul_source.like("%" + opt + "%")
											)
	return render_template('src/vul_report_list_read.html', vul_report_list_result=vul_report_list_result)


@src.route('/vul_report_read/<id>')
def vul_report_read(id):
	vul_report = VulReport.query.get_or_404(id)
	if vul_report.vul_status != u'完成':
		if current_user.is_authenticated:
			if current_user.role_name==u'超级管理员' or current_user.role_name==u'安全管理员':
				pass
			else:
				if vul_report.vul_status == u'未审核':
					abort(403)
				else:
					email_list = get_email_list(id)
					if current_user.email not in [email_list[0][1], email_list[1][1]]:
						abort(403)
		else:
			return redirect( url_for('auth.login', next=url_for('src.vul_report_read', id=id)) )

	return render_template('src/vul_report_read.html', vul_report=vul_report)


@src.route('/vul_report_delete/<id>')
@permission_required('src.vul_report_delete')
def vul_report_delete(id):
	vul_report_del = VulReport.query.get_or_404(id)
	db.session.delete(vul_report_del)
	flash('Delete vul_report success.')
	return redirect(url_for('src.vul_report_list_read'))


@src.route('/vul_report_review/<id>', methods=['GET','POST'])
@permission_required('src.vul_report_review')
def vul_report_review(id):
	form = VulReportReviewForm()
	vul_report_rv = VulReport.query.get_or_404(id)
	author_get = User.query.filter_by(name=vul_report_rv.author).first()
	asset_get = Asset.query.filter_by(domain=vul_report_rv.related_asset).first()
	email_list = get_email_list(id)
	

	#Post提交审核完成，发送通告邮件
	if form.validate_on_submit():
		vul_report_rv.related_vul_type = form.related_vul_type.data
		vul_report_rv.grant_rank = form.grant_rank.data
		vul_report_rv.start_date = form.start_date.data
		vul_report_rv.end_date = form.end_date.data

		#设置风险值
		risk_score, days = get_risk_score_and_end_date(int(vul_report_rv.grant_rank), asset_get)
		vul_report_rv.risk_score = risk_score

		flash('vul report review success!')

		#发送审核后的漏洞通告邮件
		for p in email_list:
			send_email(p[1], 'A new vul alert', 'src/email/new_vul_alert', p=p, vul_report_rv=vul_report_rv)
			flash('send email to %s success!' %p[0])
		vul_report_rv.vul_status = u'已通告'
		return redirect(url_for('src.vul_report_list_read'))


	risk_score, days = get_risk_score_and_end_date(int(vul_report_rv.grant_rank), asset_get)

	#通告日期
	start_date = datetime.date.today()
	
	#限定修复日期
	end_date = datetime.date.today() + datetime.timedelta(days=days)


	form.related_vul_type.data = vul_report_rv.related_vul_type
	form.grant_rank.data = str(vul_report_rv.grant_rank)
	form.start_date.data = start_date
	form.end_date.data = end_date
	return render_template('src/vul_report_review.html', form=form, vul_report_rv=vul_report_rv, 
							asset_get=asset_get, email_list=email_list, risk_score=risk_score)


@src.route('/vul_report_review_ajax/<id>', methods=['POST'])
@permission_required('src.vul_report_review_ajax')
def vul_report_review_ajax(id):
	vul_report_rv = VulReport.query.get_or_404(id)
	asset_get = Asset.query.filter_by(domain=vul_report_rv.related_asset).first()
	risk_score, days = get_risk_score_and_end_date(int(request.form.get('grant_rank')), asset_get)
	end_date = datetime.date.today() + datetime.timedelta(days=days)
	return jsonify(risk_score=str(risk_score), end_date=end_date.strftime('%Y-%m-%d'))


@src.route('/vul_report_dev_finish/<id>', methods=['GET','POST'])
@permission_required('src.vul_report_dev_finish')
def vul_report_dev_finish(id):
	form = VulReportDevFinishForm()
	vul_report_df = VulReport.query.get_or_404(id)
	if (vul_report_df.vul_status != u'已通告') and (vul_report_df.vul_status != u'修复中'):
		abort(403)


	#Post提交复测申请
	if form.validate_on_submit():
		vul_log = VulLog(related_vul_id=id,
						related_user_email=current_user.email,
						action=u'申请复测',
						content=form.dev_finish_solution.data,
						)
		db.session.add(vul_log)
		flash(u'申请测试提交成功！')
		email_list = get_email_list(id)
		#成功申请复测后，发送提醒邮件给漏洞相关人员
		for p in email_list:
			send_email(p[1], u'漏洞复测申请', 'src/email/vul_re_test', p=p, vul_report_df=vul_report_df)
			flash('send email to %s success!' %p[0])
		vul_report_df.vul_status = u'复测中'
		return redirect(url_for('src.vul_report_list_read'))
	return render_template('src/vul_report_dev_finish.html', form=form, vul_report_df=vul_report_df)


@src.route('/vul_report_retest_result/<id>', methods=['GET','POST'])
@permission_required('src.vul_report_retest_result')
def vul_report_retest_result(id):
	form = VulReportRetestResultForm()
	vul_report_retest = VulReport.query.get_or_404(id)
	if vul_report_retest.vul_status != u'复测中':
		abort(403)
	asset_get = Asset.query.filter_by(domain=vul_report_retest.related_asset).first()

	if form.validate_on_submit():
		vul_report_retest.done_rank = form.done_rank.data
		#计算剩余风险值和修复天数
		risk_score, days = get_risk_score_and_end_date(int(vul_report_retest.done_rank), asset_get)
		vul_report_retest.residual_risk_score = risk_score
		
		if days == 0:
			vul_report_retest.fix_date = datetime.date.today()
			vul_report_retest.vul_status = u'完成'
		else:
			vul_report_retest.end_date = vul_report_retest.start_date + datetime.timedelta(days=days)
			vul_report_retest.vul_status = u'修复中'


		vul_log = VulLog(related_vul_id=id,
						related_user_email=current_user.email,
						action=u'复测结果提交',
						content=form.done_solution.data,
						)
		db.session.add(vul_log)
		flash(u'复测结果提交成功！')
		email_list = get_email_list(id)
		#成功提交复测结果后，发送提醒邮件给漏洞相关人员
		for p in email_list:
			send_email(p[1], u'复测结果已提交', 'src/email/vul_retest_result', p=p, vul_report=vul_report_retest, vul_log=vul_log)
			flash('send email to %s success!' %p[0])
		return redirect(url_for('src.vul_report_list_read'))

	form.done_rank.data = str(vul_report_retest.done_rank)
	form.end_date.data = vul_report_retest.end_date
	return render_template('src/vul_report_retest_result.html', form=form, 
							vul_report_retest=vul_report_retest, asset_get=asset_get)


@src.route('/vul_report_retest_ajax/<id>', methods=['POST'])
@permission_required('src.vul_report_retest_ajax')
def vul_report_retest_ajax(id):
	vul_report_retest = VulReport.query.get_or_404(id)
	if vul_report_retest.vul_status != u'复测中':
		abort(403)
	asset_get = Asset.query.filter_by(domain=vul_report_retest.related_asset).first()
	done_rank = int(request.form.get('done_rank'))

	risk_score, days = get_risk_score_and_end_date(done_rank, asset_get)

	#限定修复日期
	if days == 0:
		end_date = vul_report_retest.end_date
	else:
		end_date = vul_report_retest.start_date + datetime.timedelta(days=days)

	return jsonify(residual_risk_score=str(risk_score), end_date=end_date.strftime('%Y-%m-%d'))


def get_risk_score_and_end_date(rank, asset):
	#设置业务等级系数
	asset_level_value = 0
	if asset.level == u'一级':
		asset_level_value = 1
	elif asset.level == u'二级':
		asset_level_value = 0.9
	elif asset.level == u'三级':
		asset_level_value = 0.8
	else:
		asset_level_value = 0.7

	#设置内外网系数
	asset_inout_value = 0
	if asset.in_or_out == u'外网':
		asset_inout_value = 1
	elif asset.in_or_out == u'内网':
		asset_inout_value = 0.8
	else:
		asset_inout_value = 0

	#风险值＝rank * 业务等级系数 ＊ 风险值权重 ＊ 内外网系数
	risk_score = round(rank * asset_level_value * 5 * asset_inout_value,2)

	#计算修复天数
	if 75<risk_score<=100:
		#days = 3-5
		days = round( 5 - (risk_score-75)*0.08, 0)
	elif  50<risk_score<=75:
		#days = 7-10
		days = round( 10 - (risk_score-50)*0.12, 0)
	elif  25<risk_score<=50:
		#days = 14-20
		days = round( 20 - (risk_score-25)*0.24, 0)
	elif  0<risk_score<=25:
		#days = 21-30
		days = round( 30 - (risk_score-0)*0.36, 0)
	else:
		days = 0

	#如果系统为上线前测试，将修复天数延长至1年
	if asset.status == u'上线前':
		days = 365

	return risk_score, days


def get_email_list(vul_report_id):
	vul_report_get = VulReport.query.get_or_404(vul_report_id)
	author_get = User.query.filter_by(name=vul_report_get.author).first()
	asset_get = Asset.query.filter_by(domain=vul_report_get.related_asset).first()
	department_get = Depart.query.filter_by(department=asset_get.department).first()
	user_get = User.query.filter_by(name=asset_get.owner).first()
	email_list = [(user_get.name, user_get.email),
				(department_get.leader, department_get.email),
				(author_get.name, author_get.email),
				]

	return email_list
