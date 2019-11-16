#!/usr/bin/env python
# coding=utf-8
# Stan 2018-12-21

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
from mimetypes import MimeTypes

from flask import current_app
from flask_mail import Message

from ..app import mail


mimes = MimeTypes()


def send_email(message, recipients, subject=None, attachments=[], sender=None, forward=True):
    if not subject:
        subject = ''

    with current_app.app_context():
        msg = Message(subject,
                      recipients = recipients,
                      body = message,
                      html = message,
                      sender = sender,
                      bcc = [current_app.config.get('INDEX_REPORT_MAIL')] if forward else None
                     )

        for attachment in attachments:
            if attachment and os.path.isfile(attachment):
                with open(attachment, 'rb') as fp:
                    mime = mimes.guess_type(attachment)
                    content_type = mime[0] or 'application/octet-stream'
                    msg.attach(attachment, content_type, fp.read())

        mail.send(msg)
