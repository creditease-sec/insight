#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from app import create_app, db
from app.admin.models import Asset
from app.auth.models import LoginUser
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

# 使用指定配置初始化创建flask app
app = create_app(os.getenv('SrcPM_CONFIG') or 'default')
# 关闭flask app debug 模式
app.debug = False
# Flask-Script扩展为Flask程序添加了一个命令行解析器，并自带了一组常用选项，它还支持自定义命令
manager = Manager(app)
migrate = Migrate(app, db, compare_type=True)




def make_shell_context():
    return dict(app=app, db=db, Asset=Asset, LoginUser=LoginUser)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
	"""Run the unit test."""
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':   
    manager.run()
