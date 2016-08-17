from flask import current_app, render_template
from . import mail
from flask_mail import Message
from threading import Thread


def send_email(subject, template, **kwargs):
	app = current_app._get_current_object()
	msg = Message(app.config['SRCPM_MAIL_SUBJECT_PREFIX'] + subject,
		sender = app.config['SRCPM_MAIL_SENDER'])
	msg.recipients = kwargs['to']
	for k,v in kwargs.items():
		if k == 'cc':
			msg.cc = v
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr

def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

