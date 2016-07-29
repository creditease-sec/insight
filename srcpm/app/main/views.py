#-*- coding:utf-8 -*-
from flask import render_template
from app.src.models import VulRank
from . import main
import chartkick


@main.route('/')
def index():
	rank_hao = VulRank.query.filter_by(name=u'王昊')
	score_hao = 0
	for r_hao in rank_hao:
		score_hao += r_hao.score
	print 'score_hao=%s' %str(score_hao)

	rank_jie = VulRank.query.filter_by(name=u'万杰')
	score_jie = 0
	for r_jie in rank_jie:
		score_jie += r_jie.score
	print 'score_jie=%s' %str(score_jie)

	rank_yu = VulRank.query.filter_by(name=u'潘烁宇')
	score_yu = 0
	for r_yu in rank_yu:
		score_yu += r_yu.score
	print 'score_yu=%s' %str(score_yu)

	data = {'hao': score_hao, 'jie': score_jie, 'yu': score_yu}
	return render_template('index.html', data=data)