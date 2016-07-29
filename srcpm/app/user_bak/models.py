from .. import db


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