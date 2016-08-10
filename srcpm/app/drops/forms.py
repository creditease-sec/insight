# -*- coding:utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
    SelectField, TextField, TextAreaField, RadioField
from wtforms import ValidationError, TextField, DateField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms.widgets import CheckboxInput
from flask import request
from app.admin.models import Depart
from flask_pagedown.fields import PageDownField
from app.drops.models import Category

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
                      description=u'多个标签用逗号隔开', id='tag_id')
    content = PageDownField(u'drop内容', id='content_id')
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(DropForm, self).__init__(*args, **kwargs)
        self.category.choices = [(i.id, i.category_name)
                                 for i in Category.query.order_by(Category.id).all()]
