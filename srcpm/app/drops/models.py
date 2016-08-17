# -*- coding:utf-8 -*-
from flask_sqlalchemy import BaseQuery
from datetime import datetime
from markdown import markdown
import bleach
from .. import db
from ..auth.models import LoginUser


# drops分类表


class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True)
    drops = db.relationship('Postdrop', backref='cate', lazy='dynamic')

    # 自定义数据库初始化
    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<category name %r>' % self.category_name

# drops和标签的多对多联表
article_tags = db.Table('relationships',
                        db.Column(
                            'tag_id', db.Integer, db.ForeignKey('tags.id')),
                        db.Column(
                            'postdrop_id', db.Integer, db.ForeignKey('postdrops.id')),
                        )


# 文章标签表
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    # post = db.relationship('Post', secondary=article_tags)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<tag name %r>' % self.name


'''
    id: 主键
    drop_content: drop内容字段 Text可变长度
    drop_title: drop标题字段 字符串
    drop_name: drop名字 字符串
    drop_create_time:drop创建时间 时间类型
    view_num:阅读数 整型
    comment_count:评论数 整型
    status:状态
    author_id：作者id
    drop_modified_time:drop编辑时间
    category_id:category.id外键与category表中书据一致
    categorys:定义drop对象对于cate的反向引用
    tags:和标签的多对多关系及drop对tag的反向引用
    tags_name:标签字段，可变长度

'''
# 自定义drop查询方便，drop显示愉快素查找


class PostQuery(BaseQuery):

    def getdrop_id(self, id):
        return self.get(id)

    def getall(self):
        return self.all()

    def getdrop_byname(self, name):
        return self.filter(Postdrop.drop_name.ilike(name)).distinct().first()

    def getdrop_perpage(self, pageid, per_page):
        return self.order_by(Postdrop.drop_create_time.desc()).paginate(pageid, per_page)

    def hotdrop(self):
        return self.order_by(Postdrop.comment_count.desc(), Postdrop.view_num.desc())

    def newdrop(self):
        return self.order_by(Postdrop.drop_modified_time.desc())

    # distinct去除重复记录,db.and_链接查询语句，q是查询语句(待关键字)
    def search(self, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(Postdrop.drop_title.ilike(keyword),
                                   Postdrop.drop_content.ilike(keyword),
                                   Postdrop.tags_name.ilike(keyword)))

        q = reduce(db.and_, criteria)

        return self.filter(q).distinct()

    def search_tag(self, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(Postdrop.tags_name.ilike(keyword)))

        q = reduce(db.and_, criteria)

        return self.filter(q).distinct()


class Postdrop(db.Model):
    __tablename__ = 'postdrops'
    query_class = PostQuery
    id = db.Column(db.Integer, primary_key=True)
    drop_content = db.Column(db.Text)
    drop_content_html = db.Column(db.Text)
    drop_title = db.Column(db.String(50))
    drop_name = db.Column(db.String(50), unique=True)
    drop_create_time = db.Column(db.DateTime, default=datetime.utcnow)
    view_num = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    author_id = db.Column(db.Integer, db.ForeignKey('login_users.id'))
    drop_modified_time = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
    categorys = db.relationship('Category', backref=db.backref(
        'postdrop', lazy='dynamic'), lazy='select')
    tags = db.relationship('Tag', secondary=article_tags,
                           backref=db.backref('postdrop', lazy='dynamic'))
    tags_name = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(Postdrop, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<postdrop %r>' % self.drop_title

    def _url(self):
        return url_for('drop_byname', postname=self.drop_name)

    @staticmethod
    def on_changed_drop_content(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt'],
        }
        target.drop_content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=attrs, strip=True)
        )

db.event.listen(Postdrop.drop_content, 'set', Postdrop.on_changed_drop_content)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    comt_id = db.Column(db.Integer, db.ForeignKey('postdrops.id'))
    posts = db.relationship(
        'Postdrop', backref=db.backref('comments', lazy='dynamic'))
    author_name = db.Column(db.String(50))
    author_email = db.Column(db.String(100))
    author_ip = db.Column(db.String(20))
    comment_create_time = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    isvisible = db.Column(db.Integer, default=0)

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<comment %r>' % self.content

    @staticmethod
    def on_changed_drop_comment(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt'],
        }
        target.content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=attrs, strip=True)
        )

db.event.listen(Comment.content, 'set', Comment.on_changed_drop_comment)
# 按照页数查询


def pageby(obj, pageid, per_page, orderby):
    return obj.order_by(orderby).paginate(pageid, per_page)
