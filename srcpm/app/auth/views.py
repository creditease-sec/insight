#coding:utf-8

from flask import render_template, redirect, flash, url_for, request
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm
from .models import LoginUser
from ..admin.models import User
from ..admin.models import Role
from .. import db
from . import auth
from ..email import send_email
from flask_login import login_required, current_user, login_user, logout_user
from ..LDAPLogin import ldap_login
import json
import requests


''' LDAP登录代码样例'''
"""
@auth.route('/login_ldap', methods=['GET','POST'])
def login_ldap():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.email.data.split('@')[0]
        password = form.password.data

        lg_user = LoginUser.query.filter_by(email=form.email.data).first()

        # 超级管理员登录判定方法
        if username=='srcadmin' and lg_user.verify_password(form.password.data):
            login_user(lg_user, form.remember_me.data)
            #防止任意URL跳转到其它网站
            if request.args.get('next') is not None and ('//' in request.args.get('next')):
                return redirect(url_for('main.index'))

            return redirect(request.args.get('next') or url_for('main.index'))
        # 不是超级管理员登录
        else:
            if ldap_login(username, password):
                if lg_user:
                    login_user(lg_user, form.remember_me.data)
                else:
                    lg_user = LoginUser(email=form.email.data,
                                        username=username,
                                        password=form.password.data,
                                        confirmed=True,
                                        role_name=u'普通用户',
                                        )
                    db.session.add(lg_user)
                    db.session.commit()
                    login_user(lg_user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
            else:
                flash(u'用户名或密码错误')

    return render_template('auth/login_ldap.html', form=form)
"""


''' 登录页面 '''
@auth.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		lg_user = LoginUser.query.filter_by(email=form.email.data).first()
		if lg_user is not None and lg_user.verify_password(form.password.data):
			login_user(lg_user, form.remember_me.data)
			#防止任意URL跳转到其它网站
			if request.args.get('next') is not None and ('//' in request.args.get('next')):
				return redirect(url_for('main.index'))

			return redirect(request.args.get('next') or url_for('main.index'))
		flash(u'用户名或密码错误')
	return render_template('auth/login.html', form=form)


''' 注销功能请求 '''
@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u'您已成功退出')
	return redirect(url_for('main.index'))


''' 注册页面 '''
@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		lg_user = LoginUser(email=form.email.data, username=form.username.data, password=form.password.data)
		db.session.add(lg_user)
		db.session.commit()
		token = lg_user.generate_confirmation_token()
		send_email('Confirm Your Account', 'auth/email/confirm', to=[lg_user.email], lg_user=lg_user, token=token)
		flash(u'确认邮件已发送至您的邮箱，请到邮箱确认.')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form=form)


''' 邮件验证链接功能请求 '''
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		role_default = Role.query.filter_by(default=True).first()
		#设置默认角色
		if role_default is not None:
			current_user.role_name = role_default.role_name
			db.session.add(current_user)
		#设置关联人员姓名
		related_user = User.query.filter_by(email=current_user.email).first()
		if related_user is not None:
			current_user.related_name = related_user.name
			db.session.add(current_user)
		flash(u'您的帐号已确认成功，谢谢！')
	else:
		flash(u'确认链接失效或已过期')
	return redirect(url_for('main.index'))


''' 注册用户未验证邮箱前，只能访问auth模块和静态资源 '''
@auth.before_app_request
def before_request():
	if current_user.is_authenticated and not current_user.confirmed \
			and request.endpoint[:5] != 'auth.' \
			and request.endpoint != 'static' \
            and request.endpoint != 'src.static' \
            and request.endpoint != 'main.static' \
            and request.endpoint != 'auth.static' \
            and request.endpoint != 'drops.static':
		return redirect(url_for('auth.unconfirmed'))


''' 注册用户未进行邮箱验证提醒和重新发送确认邮件页面 '''
@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')


''' 发送确认邮件功能请求 '''
@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email('Confirm Your Account', 
		'auth/email/confirm',to=[current_user.email], lg_user=current_user, token=token)
	flash(u'确认邮件已发送至您的邮箱，请到邮箱确认.')
	return redirect(url_for('main.index'))


''' 修改密码页面 '''
@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash(u'您的密码已更新')
            return redirect(url_for('main.index'))
        else:
            flash(u'密码错误')
    return render_template("auth/change_password.html", form=form)


''' 重置密码页面 '''
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        lg_user = LoginUser.query.filter_by(email=form.email.data).first()
        if lg_user:
        	token = lg_user.generate_reset_token()
        	send_email(u'重置您的密码',
                       'auth/email/reset_password',
                       to = [lg_user.email],
                       lg_user=lg_user, token=token,
                       next=request.args.get('next'))
        	flash(u'重置密码的邮件已发送至您的邮箱')

        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


''' 重置的新密码提交验证请求 '''
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    ''' 如果是登录状态，则返回主页 '''
    if not current_user.is_anonymous:
		return redirect(url_for('main.index'))

    ''' 未登录状态下，进行重置密码验证 '''
    form = PasswordResetForm()
    if form.validate_on_submit():
        lg_user = LoginUser.query.filter_by(email=form.email.data).first()
        # 如果邮箱不存在，则返回主页
        if lg_user is None:
            return redirect(url_for('main.index'))
        # 如果token和邮箱能对应上，则重置密码成功，返回登录页面。否则返回主页
        if lg_user.reset_password(token, form.password.data):
            flash(u'您的密码已更新')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

