# -*- coding:utf-8 -*-

from datetime import datetime
from markdown import markdown
import bleach
from .. import db




# drops分类表


class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True)

    # 自定义数据库初始化
    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<category name %r>' % self.category_name

# 分类和标签的关联表
# article_tags = db.Table('relationships',
#                         db.Column(
#                             'tag_id', db.Integer, db.ForeignKey('tags.id')),
#                         db.Column(
#                             'Postdrop_id', db.Integer, db.ForeignKey('postdrops.id')),
#                         )
#
#
# 文章标签表
# class Tag(db.Model):
#     __tablename__ = 'tags'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#
#     # post = db.relationship('Post', secondary=article_tags)
#
#     def __init__(self, *args, **kwargs):
#         super(Tag, self).__init__(*args, **kwargs)
#
#     def __repr__(self):
#         return '<tag name %r>' % self.name


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
    categorys:定义drop对象的反向引用
    tags:和标签的多对多关系
    tags_name:标签字段，可变长度

'''

class Postdrop(db.Model):
    __tablename__ = 'postdrops'
    id = db.Column(db.Integer, primary_key=True)
    drop_content = db.Column(db.Text)
    drop_title = db.Column(db.String(50))
    drop_name = db.Column(db.String(50), unique=True)
    drop_create_time = db.Column(db.DateTime, default=datetime.utcnow)
    view_num = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    author_id = db.Column(db.Integer, default=1)
    drop_modified_time = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
    # categorys = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'), lazy='select')
    # tags = db.relationship('Tag', secondary=article_tags,backref=db.backref('posts', lazy='dynamic'))
    tags_name = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<postdrop %r>' % self.drop_title
