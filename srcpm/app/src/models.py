#coding:utf-8

from datetime import datetime
from markdown import markdown
import bleach
from .. import db



class VulReport(db.Model):
	__tablename__ = 'vul_reports'
	id = db.Column(db.Integer, primary_key = True)
	author = db.Column(db.String(64), index=True)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	title = db.Column(db.String(128))
	related_asset = db.Column(db.String(64))
	related_asset_inout = db.Column(db.String(64))
	related_asset_status = db.Column(db.String(64))
	related_vul_cata = db.Column(db.String(64))
	related_vul_type = db.Column(db.String(64))
	vul_self_rank = db.Column(db.Integer)
	vul_source = db.Column(db.String(64))
	vul_poc = db.Column(db.Text)
	vul_poc_html = db.Column(db.Text)
	vul_solution = db.Column(db.Text)
	vul_solution_html = db.Column(db.Text)
	grant_rank = db.Column(db.Integer)
	vul_type_level = db.Column(db.String(64))
	risk_score = db.Column(db.Float)
	person_score = db.Column(db.Integer)
	done_solution = db.Column(db.Text)
	done_rank = db.Column(db.Integer)
	residual_risk_score = db.Column(db.Float)
	vul_status = db.Column(db.String(64))
	start_date = db.Column(db.Date)
	end_date = db.Column(db.Date)
	fix_date = db.Column(db.Date)
	attack_check = db.Column(db.String(64))



	@staticmethod
	def on_changed_vul_poc(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
						'h1', 'h2', 'h3', 'p', 'img']
		attrs = {
				'*': ['class'],
				'a': ['href', 'rel'],
				'img': ['src', 'alt'],
				}
		target.vul_poc_html = bleach.linkify(bleach.clean(
							markdown(value, output_format='html'),
							tags=allowed_tags, attributes=attrs, strip=True)
							)

	@staticmethod
	def on_changed_vul_solution(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
						'h1', 'h2', 'h3', 'p', 'img']
		attrs = {
				'*': ['class'],
				'a': ['href', 'rel'],
				'img': ['src', 'alt'],
				}
		target.vul_solution_html = bleach.linkify(bleach.clean(
							markdown(value, output_format='html'),
							tags=allowed_tags, attributes=attrs, strip=True)
							)

	@staticmethod
	def on_changed_vul_self_rank(target, value, oldvalue, initiator):
		target.grant_rank = int(value)
		target.vul_status = u'未审核'
		if 0<int(value)<=5:
			target.vul_type_level = '低危'
		elif 5<int(value)<=10:
			target.vul_type_level = '中危'
		elif 10<int(value)<=15:
			target.vul_type_level = '高危'
		elif 15<int(value)<=20:
			target.vul_type_level = '严重'
		else:
			target.vul_type_level = '忽略'

	@staticmethod
	def on_changed_risk_score(target, value, oldvalue, initiator):
		if target.related_vul_type == u'输出文档':
			target.residual_risk_score = float(0)
			target.done_rank = 0
		else:
			target.residual_risk_score = float(value)
			target.done_rank = target.grant_rank

db.event.listen(VulReport.vul_poc, 'set', VulReport.on_changed_vul_poc)
db.event.listen(VulReport.vul_solution, 'set', VulReport.on_changed_vul_solution)
db.event.listen(VulReport.vul_self_rank, 'set', VulReport.on_changed_vul_self_rank)
db.event.listen(VulReport.risk_score, 'set', VulReport.on_changed_risk_score)


class VulLog(db.Model):
	__tablename__ = 'vul_logs'
	id = db.Column(db.Integer, primary_key=True)
	related_vul_id = db.Column(db.Integer)
	time = db.Column(db.DateTime, default=datetime.utcnow)
	related_user_email = db.Column(db.String(64))
	action = db.Column(db.String(64))
	content = db.Column(db.Text)


