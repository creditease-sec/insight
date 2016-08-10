# -*- coding:utf-8 -*-

from flask import render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user
from . import drops
from .forms import CateForm, DropForm
from .models import Category, Postdrop, Tag
from .. import db
from datetime import datetime
from ..decorators import permission_required
from datetime import datetime
import re

# 过滤字符串


def str_filter(str_input):

    str_output = str_input.strip()
    str_output = str_output.replace(' ', '')
    str_output = str_output.replace('\r', '')
    str_output = str_output.replace('\n', '')
    str_output = str_output.replace(u'，', ',')
    str_output = re.sub(r"alert", '', str_output, 0, re.I)
    str_output = re.sub(r"script", '', str_output, 0, re.I)
    str_output = re.sub(r";", '', str_output, 0, re.I)
    str_output = re.sub(r"&", '', str_output, 0, re.I)
    str_output = re.sub(r"'", '', str_output, 0, re.I)
    str_output = re.sub(r'"', '', str_output, 0, re.I)
    str_output = re.sub(r"<", '', str_output, 0, re.I)
    str_output = re.sub(r">", '', str_output, 0, re.I)
    str_output = re.sub(r"/", '', str_output, 0, re.I)

    return str_output

# 查询权限列表如果用户的角色和权限符合drop管理原跳转至manager页面


@drops.route('/')
@drops.route('/index')
def index():
    return render_template('drops/index.html')


@drops.route('/manager')
@permission_required('drops.manager')
def manager():
    return render_template('drops/manager.html')


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


# 删除分类
@drops.route('/delcate/<id>')
@permission_required('drops.manager')
def delcate(id):
    catepost_del = Category.query.get_or_404(id)
    db.session.delete(catepost_del)
    flash(u'删除成功')
    return redirect(url_for('drops.readcate'))


#--------drops文章---------
# 添加文章


@drops.route('/newdrops', methods=['GET', 'POST'])
@permission_required('drops.manager')
def newdrops():
    categories = Category.query.order_by(Category.id.desc()).all()
    form = DropForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            tagtemp = []
            taglist = form.tag.data.split(',')
            for i in taglist:
                tagtemp.append(Tag(name=i))
            post = Postdrop(drop_content=form.content.data,
                            drop_title=str_filter(request.form['title']),
                            drop_name=str_filter(request.form['dropname']),
                            tags_name=form.tag.data,
                            category_id=request.form['category'],
                            author_id=current_user.id)
            db.session.add(post)
            flash(u'新的drop已添加!')
            return redirect(url_for('drops.readdrops'))
    return render_template('drops/newdrops.html', categories=categories, form=form)

# 查看drop


@drops.route('/readdrops', methods=['GET', 'POST'])
@permission_required('drops.manager')
def readdrops():
    opt = request.form.get('opt', 'all')
    page = request.args.get('page', 1, type=int)
    if opt == 'all':

        pagination = Postdrop.query.order_by(Postdrop.id.desc()).paginate(
            page, per_page=10, error_out=False)
        posts = pagination.items

    else:

        pagination = Postdrop.query.filter(Postdrop.drop_title.like("%" + opt + "%")).paginate(
            page, per_page=10, error_out=False)
        posts = pagination.items

    return render_template('drops/readdrops.html', posts=posts, pagination=pagination)

# 编辑drops


@drops.route('/editdrops/<int:id>', methods=['GET', 'POST'])
@permission_required('drops.manager')
def editdrops(id):
    droppost = Postdrop.query.get_or_404(id)
    form = DropForm()
    if form.validate_on_submit():

        droppost.drop_title = form.title.data
        droppost.drop_name = form.dropname.data
        droppost.tags_name = form.tag.data
        droppost.category_id = form.category.data
        droppost.drop_content = form.content.data
        droppost.drop_modified_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        db.session.add(droppost)
        flash(u'drop已更新!')
        return redirect(url_for('drops.readdrops'))
    form.title.data = droppost.drop_title
    form.dropname.data = droppost.drop_name
    form.tag.data = droppost.tags_name
    form.category.data = droppost.category_id
    form.content.data = droppost.drop_content
    return render_template('drops/editdrops.html', form=form, id=droppost.id)

# 删除drops


@drops.route('/deldrop/<id>')
@permission_required('drops.manager')
def deldrop(id):
    droppost_del = Postdrop.query.get_or_404(id)
    db.session.delete(droppost_del)
    flash(u'删除成功')
    return redirect(url_for('drops.readdrops'))


@drops.route('/mgrdrops')
@permission_required('drops.manager')
def mgrdrops():
    return render_template('drops/mgrdrops.html')
