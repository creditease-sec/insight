#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" 此文件用于自动周期发送漏洞提醒邮件 """

from flask import Flask
from flask_apscheduler import APScheduler
import os
from app import create_app, db
from app.admin.models import Asset
from app.auth.models import LoginUser
from app.src.models import VulReport
from app.email import send_email
from flask_mail import Mail
import random
from app.src.views import get_email_dict
basedir = os.path.abspath(os.path.dirname(__file__))

# Flask 发送邮件App 基础配置类
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    #自动commit提交到数据库
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    #邮件标题前缀
    SRCPM_MAIL_SUBJECT_PREFIX = u'[漏洞管理平台]'
    #上传图片、Excel、Xmind路径设置
    UPLOAD_IMG_FOLDER = os.path.join(basedir, 'app/static/upload/img/')
    UPLOAD_EXCEL_FOLDER = os.path.join(basedir, 'app/static/upload/excel/')
    UPLOAD_XMIND_FOLDER = os.path.join(basedir, 'app/static/upload/xmind/')
    #平台每次发送邮件的邮件抄送列表，默认设置发送给应用安全组邮箱列表，可自行修改
    CC_EMAIL = ['it.websec.list@creditease.cn',
                'baoyingzhao@creditease.cn',
            ]
    #PERMANENT_SESSION_LIFETIME = 10
    #登录时勾选记住，cookie路径和名称设置
    REMEMBER_COOKIE_PATH = '/srcpm'
    REMEMBER_COOKIE_NAME = 'srcpm_session'
    #COOKIE_NAME = 'srcpm_session'
    #COOKIE_PATH = '/srcpm'
    #drops模块分页设置，每页显示10行
    PER_PAGE = 10
    #非drops模块分页设置，每页显示10行
    SRCPM_PER_PAGE = 10
    #主机名设置
    SERVER_NAME = 'cesec.creditease.corp'


""" 发送新通告未知悉的漏洞提醒邮件，每周一到周五上午9点30分发送 """
def job_send_new_alert_mail():
    with db.app.app_context():
        send_new_alert_mail()

""" 发送漏洞状态为未修复的漏洞提醒邮件，每周一上午9点20分发送 """
def job_send_unfinish_vul_mail():
    with db.app.app_context():
        send_unfinish_vul_mail()

""" 发送新通告未知悉的漏洞提醒邮件，每周一到周五上午9点30分发送 """
def send_new_alert_mail():
    #设置发送邮件的列表
    query = db.session.query(VulReport, Asset).filter(VulReport.related_asset==Asset.domain,
                                                        VulReport.vul_status==u'已通告').order_by(-VulReport.start_date)

    list_to_send_email = []
    for vul_report in query.all():
        email_dict = get_email_dict(vul_report[0].id)
        email_list = []
        email_list = email_dict['owner']
        email_list.append(email_dict['department_manager'])
        email_list.append(email_dict['author'])
        if email_list not in list_to_send_email:
            list_to_send_email.append(email_list)


    #遍历发送邮件列表，发送提醒邮件
    #print list_to_send_email
    #list_to_send_email = [['shengliu1@creditease.cn',],]
    for e_l in list_to_send_email:
        send_email(u'新通告漏洞提醒',
                    'src/email/vul_notify_mail_alert',
                    to=e_l,
                    cc=db.app.config['CC_EMAIL'],
                    )

""" 发送漏洞状态为未修复的漏洞提醒邮件，每周一上午9点20分发送 """
def send_unfinish_vul_mail():
    #设置发送邮件的列表
    query = db.session.query(VulReport, Asset).filter(VulReport.related_asset==Asset.domain,
                                                        VulReport.vul_status==u'修复中').order_by(-VulReport.start_date)

    list_to_send_email = []
    for vul_report in query.all():
        email_dict = get_email_dict(vul_report[0].id)
        email_list = []
        email_list = email_dict['owner']
        email_list.append(email_dict['department_manager'])
        email_list.append(email_dict['author'])
        if email_list not in list_to_send_email:
            list_to_send_email.append(email_list)


    #遍历发送邮件列表，发送提醒邮件
    #print list_to_send_email
    #list_to_send_email = [['shengliu1@creditease.cn',],]
    for e_l in list_to_send_email:
        send_email(u'修复中漏洞提醒',
                    'src/email/vul_processing_mail_alert',
                    to=e_l,
                    cc=db.app.config['CC_EMAIL'],
                    )

""" 自动发送邮件程序基本配置 """
class MailConfig(Config):
    # 平台管理员邮箱设置
    SRCPM_ADMIN = os.environ.get('SRCPM_ADMIN') or 'it.sec@creditease.cn'
    # 平台发邮件账号设置
    SRCPM_MAIL_SENDER = '安全部 <it.sec@creditease.cn>'
    # 连接 mysql URl 设置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        ''
    # 发送邮件的服务器设置，账号密码由系统变量中读取
    MAIL_SERVER = '10.160.192.8'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get(
        'MAIL_USERNAME') or 'it.sec@creditease.cn'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''

    JOBS = [
        # 每周一到周五9点30分，发送新通告漏洞提醒邮件 
        {
            'id': 'job1',
            'func': job_send_new_alert_mail,
            'trigger': {  
                    'type': 'cron',  
                    'day_of_week':"mon-fri",  
                    'hour':'1',  #标准时区时间，即北京时间9点  
                    'minute':'30',  
                    'second': '0'  
                }
        },
        # 每周一9点20分，发送修复中漏洞提醒邮件
        {
            'id': 'job2',
            'func': job_send_unfinish_vul_mail,
            'trigger': {  
                    'type': 'cron',  
                    'day_of_week':"mon",  
                    'hour':'1',  #标准时区时间，即北京时间9点 
                    'minute':'20',  
                    'second': '0'  
                }
        }
    ]

    #APScheduler配置
    SCHEDULER_API_ENABLED = True


# 创建发送邮件APP，设置模版路径，初始化配置
app = Flask(__name__,template_folder='app/templates')
app.config.from_object(MailConfig())
mail = Mail()
mail.init_app(app)
# 注册src模块蓝图，需要用到漏洞URL端点地址
from app.src import src as src_blueprint
app.register_blueprint(src_blueprint, url_prefix='/srcpm/src')


if __name__ == '__main__':
    """ 初始化db环境 """
    db.app = app
    db.init_app(app)

    """ 初始化APScheduler并启动运行"""
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run(port=8888)