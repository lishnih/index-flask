#!/usr/bin/env python
# coding=utf-8
# Stan 2019-11-15

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import current_app

from flask_mail import Message


def send_email(recipients, subject, message, sender=None):
    with current_app.app_context():
        if not sender:
            sender = current_app.config.get('MAIL_DEFAULT_SENDER', '')

            msg = Message(subject, recipients=recipients, sender=sender)
            msg.body = message
            mail.send(msg)
