from datetime import datetime
from markdown import markdown
import bleach
from .. import db



class VulRank(db.Model):
	__tablename__ = 'vul_ranks'
	id = db.Column(db.Integer, primary_key = True)
	date = db.Column(db.Date)
	name = db.Column(db.String(64))
	action = db.Column(db.String(64))
	domain = db.Column(db.String(64))
	vul_type = db.Column(db.String(64))
	vul_type_level = db.Column(db.String(64))
	vul_id = db.Column(db.String(64))
	rank = db.Column(db.Integer)
	source = db.Column(db.String(64))
	score = db.Column(db.Integer)
	validate = db.Column(db.Boolean, default=False)


class VulReport(db.Model):
	__tablename__ = 'vul_reports'
	id = db.Column(db.Integer, primary_key = True)
	author = db.Column(db.String(64), index=True)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	title = db.Column(db.String(128))
	related_asset = db.Column(db.String(64))
	related_vul_type = db.Column(db.String(64))
	vul_self_rank = db.Column(db.Integer)
	vul_self_level = db.Column(db.String(64))
	vul_source = db.Column(db.String(64))
	vul_poc = db.Column(db.Text)
	vul_poc_html = db.Column(db.Text)
	vul_solution = db.Column(db.Text)
	vul_solution_html = db.Column(db.Text)


	@staticmethod
	def on_changed_vul_poc(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
						'h1', 'h2', 'h3', 'p']
		target.vul_poc_html = bleach.linkify(bleach.clean(
							markdown(value, output_format='html'),
							tags=allowed_tags, strip=True)
							)

	@staticmethod
	def on_changed_vul_solution(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
						'h1', 'h2', 'h3', 'p']
		target.vul_solution_html = bleach.linkify(bleach.clean(
							markdown(value, output_format='html'),
							tags=allowed_tags, strip=True)
							)


db.event.listen(VulReport.vul_poc, 'set', VulReport.on_changed_vul_poc)
db.event.listen(VulReport.vul_solution, 'set', VulReport.on_changed_vul_solution)


