#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from app import create_app, db
from app.admin.models import Asset
from app.auth.models import LoginUser
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('SrcPM_CONFIG') or 'default')
app.debug = False
manager = Manager(app)
migrate = Migrate(app, db, compare_type=True)

"""
if os.path.exists('.env'):
    print 'Importing environment from .env...'
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]
"""



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
