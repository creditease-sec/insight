from .. import db

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key = True)
	role_name = db.Column(db.String(64), unique = True)
	default = db.Column(db.Boolean, default=False)

	def __repr__(self):
		return '<Role %r>' % self.role_name


class Permission(db.Model):
	__tablename__ = 'permissions'
	id = db.Column(db.Integer, primary_key = True)
	role_name = db.Column(db.String(64))
	have_perm = db.Column(db.String(64)) 

	def __repr__(self):
		return '<Permission %r>' % self.role_name


class Depart(db.Model):
	__tablename__ = 'departs'
	id = db.Column(db.Integer, primary_key = True)
	department = db.Column(db.String(64), unique=True, index=True)
	leader = db.Column(db.String(64))
	email = db.Column(db.String(64), index=True)


class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), index=True)
	email = db.Column(db.String(64), unique=True, index=True)
	department = db.Column(db.String(64))


class Asset(db.Model):
	__tablename__ = 'assets'
	id = db.Column(db.Integer, primary_key = True)
	sysname = db.Column(db.String(64))
	domain = db.Column(db.String(64), unique = True, index=True)
	back_domain = db.Column(db.String(100))
	web_or_int = db.Column(db.String(64))
	is_http = db.Column(db.Boolean, default=False)
	is_https = db.Column(db.Boolean, default=False)
	in_or_out = db.Column(db.String(64))
	level = db.Column(db.String(64))
	department = db.Column(db.String(64))
	owner = db.Column(db.String(64))
	status = db.Column(db.String(64))
	chkdate = db.Column(db.Date)
	ps = db.Column(db.String(200))

class VulType(db.Model):
	__tablename__ = 'vul_types'
	id = db.Column(db.Integer, primary_key = True)
	vul_type = db.Column(db.String(64), unique = True, index=True)