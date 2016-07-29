#-*- coding:utf-8 -*-

from flask import render_template, flash, url_for, redirect, request
from . import src
from .forms import VulRankForm, VulReportForm
from .models import VulRank, VulReport
from .. import db
from datetime import datetime
from flask_login import current_user






@src.route('/vul_rank_add', methods=['GET', 'POST'])
def vul_rank_add():
	form = VulRankForm()
	if form.validate_on_submit():
		vr = VulRank(date=form.date.data, 
					name = form.name.data,
					action = form.action.data,
					domain = form.domain.data,
					vul_type = form.vul_type.data,
					vul_type_level = form.vul_type_level.data,
					vul_id = form.vul_id.data,
					rank = form.rank.data,
					source = form.source.data,
					score = form.score.data,
					validate = form.validate.data)
		db.session.add(vr)
		flash('Vul_rank %s-%s add success!' %(form.domain.data, form.vul_type.data))
		if form.vul_type.data == u'输出文档':
			ast_get = Asset.query.filter_by(domain=form.domain.data).first()
			ast_get.chkdate = form.date.data
			flash('Asset %s updated.' %ast_get.domain)
		return redirect(url_for('src.vul_rank_add'))
	return render_template('src/vul_rank_add.html', form=form)


@src.route('/vul_rank_read', methods=['GET', 'POST'])
def vul_rank_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		vul_rank_result = VulRank.query.all()
	else:
		vul_rank_result = VulRank.query.filter(VulRank.date.like("%" + opt + "%")
											| VulRank.name.like("%" + opt + "%")
											| VulRank.action.like("%" + opt + "%")
											| VulRank.domain.like("%" + opt + "%")
											| VulRank.vul_type.like("%" + opt + "%")
											| VulRank.vul_type_level.like("%" + opt + "%")
											| VulRank.vul_id.like("%" + opt + "%")
											| VulRank.source.like("%" + opt + "%")
											| VulRank.validate.like("%" + opt + "%")
											)
	return render_template('src/vul_rank_read.html', vul_rank_result=vul_rank_result)


@src.route('/vul_rank_modify/<id>', methods=['GET', 'POST'])
def vul_rank_modify(id):
	form = VulRankForm()
	vul_rank_get = VulRank.query.get_or_404(id)
	if form.validate_on_submit():
		vul_rank_get.date = form.date.data
		vul_rank_get.name = form.name.data
		vul_rank_get.action = form.action.data
		vul_rank_get.domain = form.domain.data
		vul_rank_get.vul_type = form.vul_type.data
		vul_rank_get.vul_type_level = form.vul_type_level.data
		vul_rank_get.vul_id = form.vul_id.data
		vul_rank_get.rank = form.rank.data
		vul_rank_get.source = form.source.data
		vul_rank_get.score = form.score.data
		vul_rank_get.validate = form.validate.data
		flash('The vul_rank has been updated. ')
		return redirect(url_for('src.vul_rank_read'))
	form.date.data = vul_rank_get.date
	form.name.data = vul_rank_get.name
	form.action.data = vul_rank_get.action
	form.domain.data = vul_rank_get.domain
	form.vul_type.data = vul_rank_get.vul_type
	form.vul_type_level.data = vul_rank_get.vul_type_level
	form.vul_id.data = vul_rank_get.vul_id
	form.rank.data = vul_rank_get.rank
	form.source.data = vul_rank_get.source
	form.score.data = vul_rank_get.score
	form.validate.data = vul_rank_get.validate
	return render_template('src/vul_rank_modify.html', form=form, id = vul_rank_get.id)

@src.route('/vul_rank_delete/<id>')
def vul_rank_delete(id):
	vul_rank_del = VulRank.query.get_or_404(id)
	db.session.delete(vul_rank_del)
	flash('Delete vul_rank success.')
	return redirect(url_for('src.vul_rank_read'))


#-------------漏洞报告模块------------------------------------------------------------------------------

@src.route('/vul_report_add', methods=['GET', 'POST'])
def vul_report_add():
	form = VulReportForm()
	if form.validate_on_submit():
		vul_rpt = VulReport(author=current_user.related_name, 
					title = form.title.data,
					related_asset = form.related_asset.data,
					related_vul_type = form.related_vul_type.data,
					vul_self_rank = form.vul_self_rank.data,
					vul_self_level = form.vul_self_level.data,
					vul_source = form.vul_source.data,
					vul_poc = form.vul_poc.data,
					vul_solution  = form.vul_solution .data,
					)
		db.session.add(vul_rpt)
		flash('Vul_report %s-%s add success!' %(current_user.related_name, form.title.data))
		return redirect(url_for('src.vul_report_add'))
	return render_template('src/vul_report_add.html', form=form)


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
											| VulReport.related_vul_type.like("%" + opt + "%")
											| VulReport.vul_self_level.like("%" + opt + "%")
											| VulReport.vul_source.like("%" + opt + "%")
											)
	return render_template('src/vul_report_list_read.html', vul_report_list_result=vul_report_list_result)