#coding:utf-8
from .. import db
from flask_login import UserMixin, current_app, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from .. import login_manager
from ..admin.models import Permission, Asset, Depart


''' 注册用户表 '''
class LoginUser(UserMixin, db.Model):
	__tablename__ = 'login_users'
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(64), unique = True, index = True)
	password_hash = db.Column(db.String(128))
	role_name = db.Column(db.String(64))
	confirmed = db.Column(db.Boolean, default=False)
	related_name = db.Column(db.String(64))

	''' 判断该注册用户是否存在对应权限，从后台数据库中查询该用户角色是否有对应权限 '''
	def can(self, permissions):
		if self.role_name == u'超级管理员':
			return True
		perm_get = Permission.query.filter_by(role_name=self.role_name, have_perm=permissions).first()
		if perm_get is None:
			return False
		else:
			return True

	''' 计算用户所拥有相应漏洞状态下的漏洞数量 '''
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
					vul_report_list += query.filter(Asset.department==department.department).all()
			else:
				vul_report_list = query.filter(Asset.owner.like("%" + self.email + "%")).all()
			count = len(vul_report_list)
		return count


	''' 产生用户注册成功后邮箱确认链接中的token '''
	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id})

	''' 产生重置密码链接中的token '''
	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id})

	''' 重置密码提交新密码时，确认token和重置的邮箱账号是否一致，一致才可以重置密码成功 '''
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

	''' 对password赋值时，实际是存储密码hash值到password_hash属性中 '''
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	''' 确认邮箱验证链接是否正确 '''
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

	''' 验证注册用户的密码是否正确 '''
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<LoginUser %r>' % self.username


''' 匿名用户，即未登录用户类 '''
class AnonymousUser(AnonymousUserMixin):
	# 未登录用户默认没有系统中设置的权限
	def can(self, permissions):
		return False

	# 未登录用户不是管理员
	def is_administrator(self):
		return False

login_manager.anonymous_user = AnonymousUser


''' 加载登录用户对象 '''
@login_manager.user_loader
def load_user(lg_user_id):
	return LoginUser.query.get(int(lg_user_id))