#coding:utf-8
from flask import Flask,  render_template
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_moment import Moment
from flask_apscheduler import APScheduler
import datetime
#import logging
#logging.basicConfig()


bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login_ldap'
pagedown = PageDown()
moment = Moment()
scheduler = APScheduler()


def create_app(config_name):
    app = Flask(__name__)
    app.jinja_env.add_extension("chartkick.ext.charts")
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    moment.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

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

