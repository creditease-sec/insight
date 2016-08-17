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
		flash('Invalid username or password.')
	return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		lg_user = LoginUser(email=form.email.data, username=form.username.data, password=form.password.data)
		db.session.add(lg_user)
		db.session.commit()
		token = lg_user.generate_confirmation_token()
		send_email('Confirm Your Account', 'auth/email/confirm', to=[lg_user.email], lg_user=lg_user, token=token)
		flash('A confirmation email has been sent to you by email.')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form=form)


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
		flash('You have confirmed your account. Thanks!')
	else:
		flash('The confirmation link is invalid or has expired.')
	return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
	if current_user.is_authenticated and not current_user.confirmed \
			and request.endpoint[:5] != 'auth.' \
			and request.endpoint != 'static':
		print 'is_authenticated: %s' %str(current_user.is_authenticated)
		print 'current_user.confirmed: %s' % current_user.confirmed
		return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email('Confirm Your Account', 
		'auth/email/confirm',to=[current_user.email], lg_user=current_user, token=token)
	flash('A new confirmation email has been sent to you by email.')
	return redirect(url_for('main.index'))

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        lg_user = LoginUser.query.filter_by(email=form.email.data).first()
        if lg_user:
        	token = lg_user.generate_reset_token()
        	send_email(lg_user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       lg_user=lg_user, token=token,
                       next=request.args.get('next'))
        	flash('An email with instructions to reset your password has been sent to you.')

        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		lg_user = LoginUser.query.filter_by(email=form.email.data).first()
		if lg_user is None:
			return redirect(url_for('main.index'))
		if lg_user.reset_password(token, form.password.data):
			flash('Your password has been updated.')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form=form)