#coding:utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SRCPM_MAIL_SUBJECT_PREFIX = u'[漏洞管理平台]'
    UPLOAD_IMG_FOLDER = os.path.join(basedir, 'app/static/upload/img/')
    PER_PAGE = 10
    UPLOAD_EXCEL_FOLDER = os.path.join(basedir, 'app/static/upload/excel/')
    UPLOAD_XMIND_FOLDER = os.path.join(basedir, 'app/static/upload/xmind/')
    CC_EMAIL = ['IT.set.list@creditease.cn']


    @staticmethod
    def init_app(app):
        pass

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SRCPM_ADMIN = os.environ.get('SRCPM_ADMIN') or '75065472@qq.com'
    SRCPM_MAIL_SENDER = '信息系统安全部 <sec_creditease@sina.com>'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        ''
    MAIL_SERVER = 'smtp.sina.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get(
        'MAIL_USERNAME') or 'sec_creditease@sina.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''


"""
	SCHEDULER_VIEWS_ENABLED = True

	JOBS = [
        {
            'id': 'job1',
            'func': 'app.src.views:weekly_mail',
            'trigger': 'interval',
            'seconds': 10,
        }
    ]
"""


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    DEBUG = False
    SRCPM_ADMIN = os.environ.get('SRCPM_ADMIN') or 'it.sec@creditease.cn'
    SRCPM_MAIL_SENDER = '信息系统安全部 <it.sec@creditease.cn>'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        ''
    MAIL_SERVER = '10.160.192.8'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get(
        'MAIL_USERNAME') or 'it.sec@creditease.cn'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
