#!/usr/bin/env python
# coding=utf-8
# Stan 2018-12-21

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask_mail import Message

from ..app import app, celery, mail


@celery.task(bind=True)
def send_email_async(self, recipients, subject, message, sender=None):
    if not sender:
        sender = app.config.get('MAIL_DEFAULT_SENDER', '')

    with app.app_context():
        msg = Message(subject, recipients=recipients, sender=sender)
        msg.body = message
        mail.send(msg)

    return {
        'current': 1,
        'total': 1,
        'status': 'Message sent!',
        'result': "Message '{0}' sent!".format(subject),
    }
