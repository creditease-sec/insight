#coding:utf-8
from .. import db
from flask_login import UserMixin, current_app, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from .. import login_manager
from ..admin.models import Permission, Asset, Depart


class LoginUser(UserMixin, db.Model):
	__tablename__ = 'login_users'
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(64), unique = True, index = True)
	password_hash = db.Column(db.String(128))
	role_name = db.Column(db.String(64))
	confirmed = db.Column(db.Boolean, default=False)
	related_name = db.Column(db.String(64))

	def can(self, permissions):
		if self.role_name == u'超级管理员':
			return True
		perm_get = Permission.query.filter_by(role_name=self.role_name, have_perm=permissions).first()
		if perm_get is None:
			return False
		else:
			return True

	def count(self, vul_status):
		from ..src.models import VulReport
		count = 0
		if self.role_name == u'超级管理员' or self.role_name == u'安全管理员':
			query = VulReport.query.filter_by(vul_status=vul_status)
			count = query.count()
		elif self.role_name == u'安全人员':
			query = VulReport.query.filter_by(vul_status=vul_status, author=self.email)
			count = query.count()
		elif self.role_name == u'普通用户':
			query = db.session.query(VulReport, Asset).filter(VulReport.related_asset==Asset.domain,
				   												VulReport.vul_status==vul_status)
			#判断普通用户是否为部门经理，部门经理有权限查看部门所有漏洞
			department_list = Depart.query.filter_by(email=self.email).all()
			if department_list:
				vul_report_list = []
				for department in department_list:
					vul_report_list = [] + query.filter(Asset.department==department.department).all()
			else:
				vul_report_list = query.filter(Asset.owner.like("%" + self.email + "%")).all()
			count = len(vul_report_list)
		return count


	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id})

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id})

	def reset_password(self, token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.id:
			return False
		self.password = new_password
		db.session.add(self)
		return True

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<LoginUser %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(lg_user_id):
	return LoginUser.query.get(int(lg_user_id))