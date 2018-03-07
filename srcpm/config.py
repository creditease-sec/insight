#coding:utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Flask App基础配置类
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
    #公司邮箱后缀限制，只能使用公司邮箱注册账号。
    CORP_MAIL = '@creditease.cn'
    #平台每次发送邮件的邮件抄送列表，默认设置发送给应用安全组邮箱列表，可自行修改
    '''
    示例：
    CC_EMAIL = ['xxx1@creditease.cn',
                'xxx2@creditease.cn',
            ]
    '''
    CC_EMAIL = [
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


    @staticmethod
    def init_app(app):
        pass

# 以开发模式的配置运行，使用测试邮件服务器，并开启debug模式
class DevelopmentConfig(Config):
    DEBUG = True
    # 平台管理员邮箱设置
    # SRCPM_ADMIN = os.environ.get('SRCPM_ADMIN') or 'admin@admin.com'
    # 平台发邮件账号设置
    SRCPM_MAIL_SENDER = '安全部 <sec_creditease@sina.com>'
    # 连接 mysql URl 设置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        ''
    # 发送邮件的服务器设置，账号密码由系统变量中读取
    MAIL_SERVER = 'smtp.sina.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get(
        'MAIL_USERNAME') or 'sec_creditease@sina.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''


# 以生产模式的配置运行，使用生产邮件服务器，并关闭debug模式
class ProductionConfig(Config):
    DEBUG = False
    # 平台管理员邮箱设置
    # SRCPM_ADMIN = os.environ.get('SRCPM_ADMIN') or 'admin@admin.com'
    # 平台发邮件账号设置
    SRCPM_MAIL_SENDER = '安全部 <xxx@creditease.cn>'
    # 连接 mysql URl 设置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        ''
    # 发送邮件的服务器设置，账号密码由系统变量中读取
    MAIL_SERVER = 'x.x.x.x'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get(
        'MAIL_USERNAME') or 'xxx@creditease.cn'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''


# 单元测试模式
class TestingConfig(Config):
    TESTING = True
    # 连接 mysql URl 设置
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
