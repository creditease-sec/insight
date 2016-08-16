# -*- coding:utf-8 -*-

from flask import render_template, flash, url_for, redirect, request, current_app, session, jsonify, abort
from flask_login import login_required, current_user, current_app, login_user
from . import drops
from .forms import CateForm, DropForm, UploadImgForm, CommentForm
from ..auth.forms import LoginForm
from ..auth.models import LoginUser
from .models import Category, Postdrop, Tag, pageby, PostQuery, Comment
from .. import db
from datetime import datetime
from ..decorators import permission_required
from random import shuffle
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


#-----------------------上传图片----------------------------------------------

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@drops.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        lg_user = LoginUser.query.filter_by(email=form.email.data).first()
        if lg_user is not None and lg_user.verify_password(form.password.data):
            login_user(lg_user, form.remember_me.data)
            # 防止任意URL跳转到其它网站
            if request.args.get('next') is not None and ('//' in request.args.get('next')):
                return redirect(url_for('main.index'))

            return redirect(request.args.get('next', url_for('drops.index')))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


# 最后返回文件名


@drops.route('/upload_img', methods=['POST'])
@permission_required('src.upload_img')
def upload_img():
    up_img_file = request.files['upload']
    if up_img_file and allowed_file(up_img_file.filename):
        img_type = up_img_file.filename.rsplit('.', 1)[1]
        save_filename = datetime.now().strftime('%Y%m%d%H%M%s') + '.' + img_type
        up_img_file.save(current_app.config[
                         'UPLOAD_IMG_FOLDER'] + save_filename)
        session['filename'] = url_for(
            'static', filename='upload/img/' + save_filename)
        return jsonify(result=session['filename'])


#--------前台展示模块---------


# 查询权限列表如果用户的角色和权限符合drop管理原跳转至manager页面


@drops.route('/')
@drops.route('/index')
@drops.route('/page/<int:pageid>')
def index(pageid=1):
    per_page = 5
    categorys = Category.query.all()
    p = Postdrop.query.getdrop_perpage(pageid, per_page)
    hot = Postdrop.query.hotdrop()[:20]
    new = Postdrop.query.newdrop()[:20]

    tag = Tag.query.all()
    shuffle(tag)
    tag = tag[:20]

    comments = Comment.query.order_by(Comment.comment_create_time.desc())[:20]
    drops = p.items
    if not p.total:
        pagination = [0]
    elif p.total % per_page:
        pagination = range(1, p.total / per_page + 2)
    else:
        pagination = range(1, p.total / per_page + 1)

    return render_template('drops/index.html',
                           categorys=categorys,
                           drops=drops,
                           hotdrops=hot,
                           newdrops=new,
                           tags=tag,
                           comments=comments,
                           pageid=pageid,
                           pagination=pagination[pageid - 1:pageid + 10],
                           last_page=pagination[-1],
                           nav_current="index"
                           )

#分类目录
@drops.route('/category/<int:cateid>')
@drops.route('/category/<int:cateid>/page/<int:pageid>')

def category(cateid=1, pageid=1):
    per_page=5
    categorys = Category.query.all()
    hot = Postdrop.query.hotdrop()[:10]
    new = Postdrop.query.newdrop()[:10]
    tag = Tag.query.all()
    shuffle(tag)
    tag = tag[:10]
    comments = Comment.query.order_by(Comment.comment_create_time.desc())[:20]

    cate = Category.query.get_or_404(cateid)

    p = pageby(cate.postdrop, pageid, per_page, Postdrop.drop_create_time.desc())

    drops = p.items
    if not p.total:
        pagination = [0]
    elif p.total % per_page:
        pagination = range(1, p.total / per_page + 2)
    else:
        pagination = range(1, p.total / per_page + 1)

    return render_template('drops/category.html',
                           id=cateid,
                           cate=cate,
                           categorys=categorys,
                           drops=drops,
                           hotdrops=hot,
                           newdrops=new,
                           tags=tag,
                           comments=comments,
                           pageid=pageid,
                           pagination=pagination[pageid - 1:pageid + 10],
                           last_page=pagination[-1]
                           )

#标签目录
@drops.route('/tag/<int:tagid>')
@drops.route('/tag/<int:tagid>/page/<int:pageid>')

def tag(tagid=1, pageid=1):
    per_page=5
    categorys = Category.query.all()
    hot = Postdrop.query.hotdrop()[:20]
    new = Postdrop.query.newdrop()[:20]
    tag = Tag.query.all()
    shuffle(tag)
    tag = tag[:20]
    comments = Comment.query.order_by(Comment.comment_create_time.desc())[:20]

    tagall = Tag.query.get_or_404(tagid)
    name = tagall.name
    p = Postdrop.query.search_tag(name)
    p = pageby(p, pageid, per_page, Postdrop.drop_create_time.desc())

    drops = p.items
    if not p.total:
        pagination = [0]
    elif p.total % per_page:
        pagination = range(1, p.total / per_page + 2)
    else:
        pagination = range(1, p.total / per_page + 1)

    return render_template('/drops/tag.html',
                           id=tagid,
                           tagall=tagall,
                           categorys=categorys,
                           drops=drops,
                           hotdrops=hot,
                           newdrops=new,
                           tags=tag,
                           comments=comments,
                           pageid=pageid,
                           pagination=pagination[pageid - 1:pageid + 10],
                           last_page=pagination[-1]
                           )


# id drop固定链接
@drops.route('/drop/<int:postid>')
def drop(postid=5):
    categorys = Category.query.all()
    hot = Postdrop.query.hotdrop()[:5]
    new = Postdrop.query.newdrop()[:5]

    tag = Tag.query.all()
    shuffle(tag)
    tag = tag[:20]
    # commentss = Comment.query.order_by(Comment.comment_create_time.desc())[:20]
    drop = Postdrop.query.getall()
    shuffle(drop)
    drop = drop[:5]

    post = Postdrop.query.get_or_404(postid)
    authorname = LoginUser.query.filter_by(id=post.author_id).first()
    form = CommentForm()
    postcoments = post.comments.all()
    post.view_num += 1
    db.session.commit()
    return render_template('drops/drops.html',
                           post=post,
                           drop=drop,
                           categorys=categorys,
                           hotdrops=hot,
                           newdrops=new,
                           tags=tag,
                           authorname=authorname,
                        #    comments=commentss,
                           postcoments=postcoments,
                           form=form
                           )

# drop_name固定链接


@drops.route('/drop/<postname>.html')
def drop_byname(postname):
    categorys = Category.query.all()
    hot = Postdrop.query.hotdrop()[:20]
    new = Postdrop.query.newdrop()[:20]

    tag = Tag.query.all()
    shuffle(tag)
    tag = tag[:20]
    #comments = Comment.query.all()[:20]
    drop = Postdrop.query.getall()

    shuffle(drop)
    drop = drop[:5]

    post = Postdrop.query.getdrop_byname(postname)
    authorname = LoginUser.query.filter_by(id=post.author_id).first()

    if not post:
        abort(404)
    form = CommentForm()
    postcoments = post.comments.all()
    post.view_num += 1
    db.session.commit()

    return render_template('drops/drops.html',
                           post=post,
                           drop=drop,
                           categorys=categorys,
                           hotdrops=hot,
                           newdrops=new,
                           tags=tag,
                           authorname=authorname,
                           #comments=comments,
                           postcoments=postcoments,
                           form=form
                           )


# 评论
@drops.route('/addcomment', methods=['GET', 'POST'])
def addcomment():
    form = CommentForm()

    if form.validate_on_submit():
        author_ip = request.remote_addr
        comment = Comment(author_ip=author_ip,
                          author_name=form.author_name.data or author_ip,
                          author_email=form.author_email.data,
                          content=form.content.data,
                          comt_id=request.form['comt_id']
                          )

        db.session.add(comment)
        if comment.comt_id:
            post = Postdrop.query.getdrop_id(comment.comt_id)
            post.comment_count += 1
            db.session.commit()
            return redirect(url_for('drops.drop', postid=comment.comt_id))



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
            page, per_page=current_app.config['PER_PAGE'], error_out=False)
        posts = pagination.items

    else:

        pagination = Category.query.filter(Category.category_name.like("%" + opt + "%")).paginate(
            page, per_page=current_app.config['PER_PAGE'], error_out=False)
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
            post = Postdrop(tags=tagtemp,
                            drop_content=form.content.data,
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
            page, per_page=current_app.config['PER_PAGE'], error_out=False)
        posts = pagination.items

    else:

        pagination = Postdrop.query.filter(Postdrop.drop_title.like("%" + opt + "%")).paginate(
            page, per_page=current_app.config['PER_PAGE'], error_out=False)
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
        droppost.drop_modified_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
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


# @drops.route('/mgrdrops')
# @permission_required('drops.manager')
# def mgrdrops():
#     return render_template('drops/mgrdrops.html')
