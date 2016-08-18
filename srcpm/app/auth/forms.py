#coding:utf-8
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from .models import LoginUser


class LoginForm(Form):
	email = StringField(u'邮箱', validators=[Required(), 
											Length(1, 64), Email()])
	password = PasswordField(u'密码', validators=[Required()])
	remember_me = BooleanField(u'记住登录')
	submit = SubmitField(u'登录')


class RegistrationForm(Form):
	email = StringField(u'邮箱', validators=[Required(), Length(1,64),Email()])
	username = StringField(u'用户名', validators=[Required(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
										'Usernames must have only letters, numbers, dots or underscores')])
	password = PasswordField(u'密码', validators=[
							Required(), EqualTo('password2', message=u'密码不一致')])
	password2 = PasswordField(u'确认密码', validators=[Required()])
	submit = SubmitField(u'注册')

	def validate_email(self, field):
		#if field.data[-7:] != '@qq.com':
		#	raise ValidationError('Email must endwith \'@qq.com\'')
		if LoginUser.query.filter_by(email=field.data).first():
			raise ValidationError(u'邮箱已经存在')

	def validate_username(self, field):
		if LoginUser.query.filter_by(username=field.data).first():
			raise ValidationError(u'用户名已被使用')


class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[Required()])
    password = PasswordField(u'新密码', validators=[
        Required(), EqualTo('password2', message=u'密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'修改密码')


class PasswordResetRequestForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField(u'重置密码')
    

class PasswordResetForm(Form):
	email = StringField(u'邮箱', validators=[Required(), Length(1, 64),
						Email()])
	password = PasswordField(u'新密码', validators=[
			Required(), EqualTo('password2', message=u'密码不一致')])
	password2 = PasswordField(u'确认密码', validators=[Required()])
	submit = SubmitField(u'重置密码')

	def validate_email(self, field):
		if LoginUser.query.filter_by(email=field.data).first() is None:
			raise ValidationError(u'此邮箱未注册')