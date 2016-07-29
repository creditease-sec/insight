#-*- coding:utf-8 -*-

from flask import render_template, flash, url_for, redirect, request
from .forms import DepartForm, UserForm
from .models import Depart, User
from . import user
from .. import db




@user.route('/depart_add', methods=['GET', 'POST'])
def depart_add():
	form = DepartForm()
	if form.validate_on_submit():
		d = Depart(department=form.department.data, 
					leader=form.leader.data,
					email=form.email.data)
		db.session.add(d)
		flash('Depart %s add success!' %form.department.data)
		return redirect(url_for('user.depart_add'))
	return render_template('user/depart_add.html', form=form)


@user.route('/depart_read', methods=['GET', 'POST'])
def depart_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		depart_result = Depart.query.all()
	else:
		depart_result = Depart.query.filter(Depart.department.like("%" + opt + "%") 
											| Depart.leader.like("%" + opt + "%")
											| Depart.email.like("%" + opt + "%")
											)
	return render_template('user/depart_read.html', depart_result=depart_result)


@user.route('/depart_modify/<id>', methods=['GET', 'POST'])
def depart_modify(id):
	form = DepartForm()
	depart_get = Depart.query.get_or_404(id)
	if form.validate_on_submit():
		#depart_get.department = form.department.data
		depart_get.leader = form.leader.data
		depart_get.email = form.email.data
		flash('The department has been updated. ')
		return redirect(url_for('user.depart_read'))
	form.department.data = depart_get.department
	form.leader.data = depart_get.leader
	form.email.data = depart_get.email
	return render_template('user/depart_modify.html', form=form, id = depart_get.id)

@user.route('/depart_delete/<id>')
def depart_delete(id):
	depart_del = Depart.query.get_or_404(id)
	db.session.delete(depart_del)
	flash('Delete department success.')
	return redirect(url_for('user.depart_read'))

#－－－－－－－User模块－－－－－－－－－－－－－－－－－－－－－－

@user.route('user_add', methods=['GET', 'POST'])
def user_add():
	form = UserForm()
	if form.validate_on_submit():
		u = User(name=form.name.data, 
					email=form.email.data,
					department=form.department.data)
		db.session.add(u)
		flash('User %s add success!' %form.name.data)
		return redirect(url_for('user.user_add'))
	return render_template('user/user_add.html', form=form)


@user.route('/user_read', methods=['GET', 'POST'])
def user_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		user_result = User.query.all()
	else:
		user_result = User.query.filter(User.name.like("%" + opt + "%") 
											| User.email.like("%" + opt + "%")
											| User.department.like('%' + opt + "%")
											)
	return render_template('user/user_read.html', user_result=user_result)


@user.route('/user_modify/<id>', methods=['GET', 'POST'])
def user_modify(id):
	form = UserForm()
	user_get = User.query.get_or_404(id)
	if form.validate_on_submit():
		#user_get.email = form.email.data
		user_get.name = form.name.data
		user_get.department = form.department.data
		flash('The user has been updated. ')
		return redirect(url_for('user.user_read'))
	form.department.data = user_get.department
	form.name.data = user_get.name
	form.email.data = user_get.email
	return render_template('user/user_modify.html', form=form, id = user_get.id)

@user.route('/user_delete/<id>')
def user_delete(id):
	user_del = User.query.get_or_404(id)
	db.session.delete(user_del)
	flash('Delete user success.')
	return redirect(url_for('user.user_read'))

