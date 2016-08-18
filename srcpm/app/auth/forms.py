#coding:utf-8
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from .models import LoginUser
import re


class LoginForm(Form):
    email = StringField(u'邮箱', validators=[Required(), 
                                    Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'记住登录')
    submit = SubmitField(u'登录')


class RegistrationForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1,64),Email()])
    username = StringField(u'用户名', validators=[Required(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                            u'用户名只能包含字母、数字、下划线和点符号')])
    password = PasswordField(u'密码', validators=[
                            Required(), EqualTo('password2', message=u'密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'注册')


    def validate_email(self, field):
        if field.data[-14:] != '@creditease.cn':
            raise ValidationError(u'邮箱必须以 \'@creditease.cn\' 结尾')
        if LoginUser.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已经存在')

    def validate_username(self, field):
        if LoginUser.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被使用')

    def validate_password(self, field):
        if len(field.data) < 8 or len(field.data) > 16:
            raise ValidationError(u'密码位数不满足8到16位之间')

        pattern = re.compile('[A-Za-z]+')
        match = pattern.findall(field.data)
        if not match:
            raise ValidationError(u'密码不包含字母')

        pattern = re.compile('[0-9]+')
        match = pattern.findall(field.data)
        if not match:
            raise ValidationError(u'密码不包含数字')


class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[Required()])
    password = PasswordField(u'新密码', validators=[
                            Required(), EqualTo('password2', message=u'密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'修改密码')

    def validate_password(self, field):
        if len(field.data) < 8 or len(field.data) > 16:
            raise ValidationError(u'密码位数不满足8到16位之间')

        pattern = re.compile('[A-Za-z]+')
        match = pattern.findall(field.data)
        if not match:
            raise ValidationError(u'密码不包含字母')

        pattern = re.compile('[0-9]+')
        match = pattern.findall(field.data)
        if not match:
            raise ValidationError(u'密码不包含数字')


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

    def validate_password(self, field):
        if len(field.data) < 8 or len(field.data) > 16:
            raise ValidationError(u'密码位数不满足8到16位之间')

        pattern = re.compile('[A-Za-z]+')
        match = pattern.findall(field.data)
        if not match:
            raise ValidationError(u'密码不包含字母')

        pattern = re.compile('[0-9]+')
        match = pattern.findall(field.data)
        if not match:
            raise ValidationError(u'密码不包含数字')