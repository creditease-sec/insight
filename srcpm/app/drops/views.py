# -*- coding:utf-8 -*-

from flask import render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user
from . import drops
from .forms import CateForm
from .models import Category
from .. import db
from datetime import datetime
from ..decorators import permission_required


# 查询权限列表如果用户的角色和权限符合drop管理原跳转至manager页面


@drops.route('/manager')
@permission_required('drops.manager')
def manager():
    return render_template('drops/manager.html')


@drops.route('/mgrdrops')
@permission_required('drops.manager')
def mgrdrops():
    return render_template('drops/mgrdrops.html')

#------------drops分类----------

# 添加分类


@drops.route('/newcate', methods=['GET', 'POST'])
@permission_required('drops.manager')
def newcate():
    form = CateForm()
    if form.validate_on_submit():
        post = Category(category_name=form.catename.data)
        db.session.add(post)
        flash(u'新的分类已添加!')
        return redirect(url_for('drops.readcate'))
    return render_template('drops/newcate.html', form=form)

# 查看分类


@drops.route('/readcate', methods=['GET', 'POST'])
@permission_required('drops.manager')
def readcate():
    opt = request.form.get('opt', 'all')
    page = request.args.get('page', 1, type=int)
    if opt == 'all':

        pagination = Category.query.order_by(Category.id.desc()).paginate(
            page, per_page=10, error_out=False)
        posts = pagination.items

    else:

        pagination = Category.query.filter(Category.category_name.like("%" + opt + "%")).paginate(
            page, per_page=10, error_out=False)
        posts = pagination.items


    return render_template('drops/readcate.html', posts=posts, pagination=pagination)

# 编辑分类


@drops.route('/editcate/<int:id>', methods=['GET', 'POST'])
@permission_required('drops.manager')
def editcate(id):
    catepost = Category.query.get_or_404(id)
    form = CateForm()

    if form.validate_on_submit():
        catepost.category_name = form.catename.data
        db.session.add(catepost)
        flash(u'分类已更新!')
        return redirect(url_for('drops.readcate'))
    form.catename.data = catepost.category_name
    return render_template('drops/editcate.html', form=form, id=catepost.id)


#删除分类
@drops.route('/delcate/<id>')
@permission_required('drops.manager')
def delcate(id):
    catepost_del = Category.query.get_or_404(id)
    db.session.delete(catepost_del)
    flash(u'删除成功')
    return redirect(url_for('drops.readcate'))
