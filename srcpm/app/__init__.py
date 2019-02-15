#coding:utf-8
from flask import Flask,  render_template
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_moment import Moment
import datetime
from flask_wtf.csrf import CsrfProtect



""" 各组件初始化 """
csrf = CsrfProtect()
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
# session安全保护级别设置
login_manager.session_protection = 'basic'
# 默认登录入口
login_manager.login_view = 'auth.login'
pagedown = PageDown()
moment = Moment()


""" 根据配置选项创建Flask APP """
def create_app(config_name):
    app = Flask(__name__)
    # 使用chartkick配合falsk画报表
    app.jinja_env.add_extension("chartkick.ext.charts")
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    moment.init_app(app)

    """ 按照功能模块来组织蓝图 """
    from .index import index as index_blueprint
    app.register_blueprint(index_blueprint, url_prefix='/')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/srcpm')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/srcpm/auth')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/srcpm/admin')

    from .src import src as src_blueprint
    app.register_blueprint(src_blueprint, url_prefix='/srcpm/src')

    from .drops import drops as drops_blueprint
    app.register_blueprint(drops_blueprint, url_prefix='/srcpm/drops')

    return app

