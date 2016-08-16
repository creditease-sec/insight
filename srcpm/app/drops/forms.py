# -*- coding:utf-8 -*-

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
    SelectField, TextField, TextAreaField, RadioField, FileField
from wtforms import ValidationError, TextField, DateField, IntegerField
from wtforms.validators import Required, Length, Email, InputRequired, Regexp, EqualTo
from wtforms.widgets import CheckboxInput
from flask import request
from app.admin.models import Depart
from flask_pagedown.fields import PageDownField
from app.drops.models import Category

# 图片表单


class UploadImgForm(Form):
    upload = FileField(u'上传图片', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ]
    )
    submit = SubmitField('Submit')

# 搜索表单


class SearchForm(Form):
    search = StringField('search', validators=[Required(), Length(1, 20)])

# category表单


class CateForm(Form):
    catename = StringField(u'类别名', validators=[Required(), Length(1, 64)])
    submit = SubmitField(u'提交')


# drops提交表单

class DropForm(Form):
    title = StringField(u'标题', validators=[Required(), Length(
        1.50)], id='title_id')
    dropname = StringField(u'drop名', validators=[
                           Required(), Length(1.50)], id='dropname_id')
    category = RadioField(
        u'类型', coerce=int, id='category_id')
    tag = StringField(u'标签', validators=[Required(), Length(1.50)],
                      render_kw={"placeholder": u"多个tag用英文逗号隔开"})
    content = PageDownField(u'drop内容', id='content_id',validators=[Required(),Length(min=10)])
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(DropForm, self).__init__(*args, **kwargs)
        self.category.choices = [(i.id, i.category_name)
                                 for i in Category.query.order_by(Category.id).all()]
# 评论表单


class CommentForm(Form):
    author_name = StringField(u'Name',validators=[
                            InputRequired(message=u"Need an name"), Length(max=50)],
                            render_kw={"placeholder": u"请输入昵称"})
    author_email = StringField(u"Email",validators=[
                             InputRequired(message=u"Need an email address"),
                             Email(message=u"Need a valid email address")],
                             render_kw={"placeholder": u"请输入邮箱"})
    content = PageDownField(u"Content")
    comt_id = IntegerField()
    submit = SubmitField(u"Save")
