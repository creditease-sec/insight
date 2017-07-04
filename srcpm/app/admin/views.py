#coding:utf-8

from flask import render_template, redirect, flash, url_for, request, jsonify
from .forms import LoginForm, RoleForm, PermissionForm, UserForm, DepartForm, UserRoleForm, AssetForm, VulTypeForm
from .models import Role, Permission, User, Depart, Asset, VulType
from ..auth.models import LoginUser
from ..src.models import VulReport
from .. import db
from . import admin
from ..decorators import permission_required
import datetime


"""
@admin.route('/login', methods=['GET','POST'])
@admin.route('/', methods=['GET','POST'])
@permission_required('admin.index')
def login():
	form = LoginForm()
	return render_template('admin/login.html', form=form)
"""

@admin.route('/')
@admin.route('/index')
@permission_required('admin.index')
def index():
	return render_template('admin/index.html')


#------用户查看－－－－－－

@admin.route('/login_user_read', methods=['GET', 'POST'])
@permission_required('admin.login_user_read')
def login_user_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		login_user_result = LoginUser.query.all()
	else:
		login_user_result = LoginUser.query.filter(LoginUser.username.like("%" + opt + "%")|
													LoginUser.email.like("%" + opt + "%")
													)
	return render_template('admin/login_user_read.html', login_user_result=login_user_result)

#-------人员手动点击关联---------

@admin.route('/login_user_related/<id>')
@permission_required('admin.login_user_related')
def login_user_related(id):
	lg_user_get = LoginUser.query.get_or_404(id)
	related_user = User.query.filter_by(email=lg_user_get.email).first()
	if related_user:
		lg_user_get.related_name = related_user.name
		db.session.add(lg_user_get)
	return redirect(url_for('admin.login_user_read'))

#------用户角色修改－－－－－－

@admin.route('/login_user_modify/<id>', methods=['GET', 'POST'])
@permission_required('admin.login_user_modify')
def login_user_modify(id):
	form = UserRoleForm()
	lg_user_get = LoginUser.query.get_or_404(id)
	if form.validate_on_submit():
		lg_user_get.role_name = form.role_name.data
		flash(u'用户角色更新成功')
		return redirect(url_for('admin.login_user_read'))
	form.role_name.data = lg_user_get.role_name
	return render_template('admin/login_user_modify.html', form=form, id = lg_user_get.id)


#-------用户删除---------

@admin.route('/login_user_delete/<id>')
@permission_required('admin.login_user_delete')
def login_user_delete(id):
	lg_user_del = LoginUser.query.get_or_404(id)
	db.session.delete(lg_user_del)
	flash(u'删除用户 %s 成功' %lg_user_del.username)
	return redirect(url_for('admin.login_user_read'))


#-------角色模块--------

@admin.route('/role_add', methods=['GET','POST'])
@permission_required('admin.role_add')
def role_add():
	form = RoleForm()
	if form.validate_on_submit():
		r = Role(role_name=form.role_name.data)
		db.session.add(r)
		flash(u'角色 %s 添加成功' %form.role_name.data)
		return redirect(url_for('admin.role_read'))
	return render_template('admin/role_add.html', form=form)


@admin.route('/role_read', methods=['GET', 'POST'])
@permission_required('admin.role_read')
def role_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		role_result = Role.query.all()
	else:
		role_result = Role.query.filter(Role.role_name.like("%" + opt + "%"))
	return render_template('admin/role_read.html', role_result=role_result)


#设置默认角色
@admin.route('/role_modify/<id>')
@permission_required('admin.role_modify')
def role_modify(id):
	role = Role.query.get_or_404(id)
	#由false变为true
	if not role.default:
		role_true = Role.query.filter_by(default=True).first()
		if role_true is not None:
			role_true.default = False
			db.session.add(role_true)
			flash(u'角色 %s 修改为非默认角色' %role_true.role_name)
		role.default = True
		db.session.add(role)
		flash(u'角色 %s 修改为默认角色' %role.role_name)
	#由true变为false
	else:
		role.default = False
		db.session.add(role)
		flash(u'角色 %s 修改为非默认角色' %role.role_name)
	return redirect(url_for('admin.role_read'))


@admin.route('/perm_modify/<role_name>', methods=['GET', 'POST'])
@permission_required('admin.perm_modify')
def perm_modify(role_name):
	form = PermissionForm()
	role_perm = Permission.query.filter_by(role_name=role_name)
	if form.validate_on_submit():
		if role_perm.first() is None:
			for h_p in form.have_perm.data:
				permission = Permission(role_name=role_name,
										have_perm=h_p)
				db.session.add(permission)
				flash(u'权限 %s 添加成功' %h_p)
		else:
			for r_p_del in role_perm:
				db.session.delete(r_p_del)
			for h_p_update in form.have_perm.data:
				permission = Permission(role_name=role_name,
										have_perm=h_p_update)
				db.session.add(permission)
				flash(u'权限 %s 添加成功' %h_p_update)
		return redirect(url_for('admin.perm_modify', role_name=role_name))

	#GET请求，先查询角色的权限，放置在form表单中，显示在页面上
	form.have_perm.data=[]
	for r_p in role_perm:
		form.have_perm.data.append(r_p.have_perm)
	return render_template('admin/perm_modify.html', form=form, role_name=role_name)


#先删除角色权限、再删除角色
@admin.route('/role_perm_delete/<role_name>')
@permission_required('admin.role_perm_delete')
def role_perm_delete(role_name):
	role_perm_del = Permission.query.filter_by(role_name=role_name)
	#删除权限
	for r_p_d in role_perm_del:
		db.session.delete(r_p_d)
	flash(u'删除权限成功')
	#删除角色
	role = Role.query.filter_by(role_name=role_name).first()
	db.session.delete(role)
	flash(u'删除权限 %s 成功' %role_name)
	return redirect(url_for('admin.role_read'))


#---------------Deaprts and Users--------------

@admin.route('/depart_add', methods=['GET', 'POST'])
@permission_required('admin.depart_add')
def depart_add():
	form = DepartForm()
	if form.validate_on_submit():
		d = Depart(department=form.department.data, 
					leader=form.leader.data,
					email=form.email.data)
		db.session.add(d)
		flash(u'部门 %s 添加成功' %form.department.data)
		return redirect(url_for('admin.depart_add'))
	return render_template('admin/depart_add.html', form=form)


@admin.route('/depart_read', methods=['GET', 'POST'])
@permission_required('admin.depart_read')
def depart_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		depart_result = Depart.query.all()
	else:
		depart_result = Depart.query.filter(Depart.department.like("%" + opt + "%") 
											| Depart.leader.like("%" + opt + "%")
											| Depart.email.like("%" + opt + "%")
											)
	return render_template('admin/depart_read.html', depart_result=depart_result)


@admin.route('/depart_modify/<id>', methods=['GET', 'POST'])
@permission_required('admin.depart_modify')
def depart_modify(id):
	form = DepartForm()
	depart_get = Depart.query.get_or_404(id)
	if form.validate_on_submit():
		#depart_get.department = form.department.data
		depart_get.leader = form.leader.data
		depart_get.email = form.email.data
		flash(u'部门更新成功')
		return redirect(url_for('admin.depart_read'))
	form.department.data = depart_get.department
	form.leader.data = depart_get.leader
	form.email.data = depart_get.email
	return render_template('admin/depart_modify.html', form=form, id = depart_get.id)

@admin.route('/depart_delete/<id>')
@permission_required('admin.depart_delete')
def depart_delete(id):
	depart_del = Depart.query.get_or_404(id)
	db.session.delete(depart_del)
	flash(u'删除部门成功')
	return redirect(url_for('admin.depart_read'))

#－－－－－－－User模块－－－－－－－－－－－－－－－－－－－－－－

@admin.route('/user_add', methods=['GET', 'POST'])
@permission_required('admin.user_add')
def user_add():
	form = UserForm()
	if form.validate_on_submit():
		u = User(name=form.name.data, 
					email=form.email.data,
					department=form.department.data)
		db.session.add(u)
		user_to_login_user(u)
		flash(u'人员 %s 增加成功' %form.name.data)
		return redirect(url_for('admin.user_add'))
	return render_template('admin/user_add.html', form=form)


@admin.route('/user_read', methods=['GET', 'POST'])
@permission_required('admin.user_read')
def user_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		user_result = User.query.all()
	else:
		user_result = User.query.filter(User.name.like("%" + opt + "%") 
											| User.email.like("%" + opt + "%")
											| User.department.like('%' + opt + "%")
											)
	return render_template('admin/user_read.html', user_result=user_result)

#设置人员到员工的关联
def user_to_login_user(user):
	lg_user = LoginUser.query.filter_by(email=user.email).first()
	if lg_user:
		lg_user.related_name = user.name

@admin.route('/user_modify/<id>', methods=['GET', 'POST'])
@permission_required('admin.user_modify')
def user_modify(id):
	form = UserForm()
	user_get = User.query.get_or_404(id)
	if form.validate_on_submit():
		#user_get.email = form.email.data
		user_get.name = form.name.data
		#设置人员到员工的关联
		user_to_login_user(user_get)

		user_get.department = form.department.data
		flash(u'人员更新成功')
		return redirect(url_for('admin.user_read'))
	form.department.data = user_get.department
	form.name.data = user_get.name
	form.email.data = user_get.email
	return render_template('admin/user_modify.html', form=form, id = user_get.id)

@admin.route('/user_delete/<id>')
@permission_required('admin.user_delete')
def user_delete(id):
	user_del = User.query.get_or_404(id)
	db.session.delete(user_del)
	flash(u'删除人员成功')
	return redirect(url_for('admin.user_read'))


#------------资产模块、漏洞类型模块--------------------------------------------------------------------------

@admin.route('/assets_add', methods=['GET', 'POST'])
@permission_required('admin.assets_add')
def assets_add():
	form = AssetForm()
	if form.validate_on_submit():
		a = Asset(sysname=form.sysname.data, 
					domain=form.domain.data, 
					back_domain=form.back_domain.data, 
					web_or_int=form.web_or_int.data, 
					is_http=form.is_http.data, 
					is_https=form.is_https.data,
					in_or_out=form.in_or_out.data,
					level=form.level.data,
					business_cata=form.business_cata.data,
					department=form.department.data,
					owner=form.owner.data,
					sec_owner=form.sec_owner.data,
					status=form.status.data,
					private_data=form.private_data.data,
					count_private_data=form.count_private_data.data,
					down_time=form.down_time.data,
					secure_level=form.secure_level.data,
					ps=form.ps.data,
					#create_date=datetime.date.today(),
					#update_date=datetime.date.today(),
					)
		db.session.add(a)
		flash(u'资产 %s 添加成功' %form.domain.data)
		return redirect(url_for('admin.assets_add'))
	return render_template('admin/assets_add.html', form=form)

@admin.route('/assets_add_ajax', methods=['GET','POST'])
@permission_required('admin.assets_add_ajax')
def assets_add_ajax():
	department = request.form.get('department')
	user_list = User.query.filter_by(department=department).all()
	opt_list = []
	for user in user_list:
		opt_list.append({'name': user.name, 'email': user.email})
	return jsonify(opt_list)


@admin.route('/assets_read', methods=['GET', 'POST'])
@permission_required('admin.assets_read')
def assets_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		asset_result = Asset.query.order_by(-Asset.update_date).all()
	else:
		asset_result = Asset.query.filter(Asset.sysname.like("%" + opt + "%") 
											| Asset.domain.like("%" + opt + "%")
											| Asset.back_domain.like("%" + opt + "%")
											| Asset.web_or_int.like("%" + opt + "%")
											| Asset.in_or_out.like("%" + opt + "%")
											| Asset.level.like("%" + opt + "%")
											| Asset.secure_level.like("%" + opt + "%")
											| Asset.business_cata.like("%" + opt + "%")
											| Asset.department.like("%" + opt + "%") 
											| Asset.owner.like("%" + opt + "%")
											| Asset.sec_owner.like("%" + opt + "%")
											| Asset.status.like("%" + opt + "%")
											).order_by(-Asset.update_date)
	return render_template('admin/assets_read.html', asset_result=asset_result)


@admin.route('/assets_modify/<id>', methods=['GET', 'POST'])
@permission_required('admin.assets_modify')
def assets_modify(id):
	form = AssetForm()
	asset_get = Asset.query.get_or_404(id)
	if form.validate_on_submit():
		asset_get.sysname = form.sysname.data

		vul_report_list = VulReport.query.filter_by(related_asset=asset_get.domain)
		#更改资产的域名
		asset_get.domain = form.domain.data
		#更改关联漏洞报告的域名
		if vul_report_list.first():
			for vul_report in vul_report_list:
				vul_report.related_asset = form.domain.data

		#asset_get.root_dir = form.root_dir.data
		asset_get.back_domain = form.back_domain.data
		asset_get.web_or_int = form.web_or_int.data
		asset_get.is_http = form.is_http.data
		asset_get.is_https = form.is_https.data
		asset_get.in_or_out = form.in_or_out.data
		asset_get.level = form.level.data
		asset_get.business_cata = form.business_cata.data
		asset_get.department = form.department.data
		asset_get.owner = form.owner.data
		asset_get.sec_owner = form.sec_owner.data
		asset_get.status = form.status.data
		#asset_get.chkdate = form.chkdate.data
		asset_get.private_data = form.private_data.data
		asset_get.count_private_data = form.count_private_data.data
		asset_get.down_time = form.down_time.data
		asset_get.secure_level = form.secure_level.data
		asset_get.ps = form.ps.data
		if asset_get.update_date:
			asset_get.update_date = datetime.date.today()
		#else:
		#	asset_get.create_date = datetime.date.today()
		#	asset_get.update_date = datetime.date.today()
		flash(u'资产更新成功')
		return redirect(url_for('admin.assets_read'))
	form.sysname.data = asset_get.sysname
	form.domain.data = asset_get.domain
	#form.root_dir.data = asset_get.root_dir
	form.back_domain.data = asset_get.back_domain
	form.web_or_int.data = asset_get.web_or_int
	form.is_http.data = asset_get.is_http
	form.is_https.data = asset_get.is_https
	form.in_or_out.data = asset_get.in_or_out
	form.level.data = asset_get.level
	form.business_cata.data = asset_get.business_cata
	form.department.data = asset_get.department
	form.owner.data = asset_get.owner
	form.sec_owner.data = asset_get.sec_owner
	form.status.data = asset_get.status
	#form.chkdate.data = asset_get.chkdate
	form.private_data.data = asset_get.private_data
	form.count_private_data.data = asset_get.count_private_data
	form.down_time.data = asset_get.down_time
	form.secure_level.data = asset_get.secure_level
	form.ps.data = asset_get.ps
	return render_template('admin/assets_modify.html', form=form, id = asset_get.id)

@admin.route('/assets_delete/<id>')
@permission_required('admin.assets_delete')
def assets_delete(id):
	asset_del = Asset.query.get_or_404(id)
	db.session.delete(asset_del)
	flash(u'删除资产成功')
	return redirect(url_for('admin.assets_read'))






@admin.route('/vul_type_add', methods=['GET', 'POST'])
@permission_required('admin.vul_type_add')
def vul_type_add():
	form = VulTypeForm()
	if form.validate_on_submit():
		vt = VulType(vul_type=form.vul_type.data)
		db.session.add(vt)
		flash(u'漏洞类型 %s 添加成功' %form.vul_type.data)
		return redirect(url_for('admin.vul_type_add'))
	return render_template('admin/vul_type_add.html', form=form)


@admin.route('/vul_type_read', methods=['GET', 'POST'])
@permission_required('admin.vul_type_read')
def vul_type_read():
	opt = request.form.get('opt','all')
	if opt=='all':
		vul_type_result = VulType.query.all()
	else:
		vul_type_result = VulType.query.filter(VulType.vul_type.like("%" + opt + "%"))
	return render_template('admin/vul_type_read.html', vul_type_result=vul_type_result)


@admin.route('/vul_type_modify/<id>', methods=['GET', 'POST'])
@permission_required('admin.vul_type_modify')
def vul_type_modify(id):
	form = VulTypeForm()
	vul_type_get = VulType.query.get_or_404(id)
	if form.validate_on_submit():
		#vul_type_get.vul_type = form.vul_type.data
		flash(u'漏洞类型更新成功')
		return redirect(url_for('admin.vul_type_read'))
	form.vul_type.data = vul_type_get.vul_type
	return render_template('admin/vul_type_modify.html', form=form, id = vul_type_get.id)

@admin.route('/vul_type_delete/<id>')
@permission_required('admin.vul_type_delete')
def vul_type_delete(id):
	vul_type_del = VulType.query.get_or_404(id)
	db.session.delete(vul_type_del)
	flash(u'删除漏洞类型成功')
	return redirect(url_for('admin.vul_type_read'))







