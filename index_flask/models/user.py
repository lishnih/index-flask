#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
from datetime import datetime

from flask import url_for

from ..app import app, db, bcrypt
from ..extensions.celery_send_email_task import send_email_async


class User(db.Model):
    __tablename__ = 'users'
    __rev__ = '2018-10-21'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    company = db.Column(db.String, nullable=False, default='')
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    verified = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    home = db.Column(db.String, nullable=False, default='')

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def is_verified(self):
        return not self.verified

    def __init__(self, username, email, password=None, **kargs):
        self.username = username
        self.email = email
        self.password = self.get_password(password) if password else '-'

        for key, value in kargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.verified = self.get_verification(password)

    def __repr__(self):
        return '<User {0!r}>'.format(self.name)

    def get_id(self):
        return self.email

    def get_password(self, password):
        pw_hash = bcrypt.generate_password_hash(password)
        return pw_hash

    def change_password(self, password):
        self.password = self.get_password(password)

    def init_env(self, send=True):
        self.home = "{0}/id{1}".format(app.config['INDEX_USERS_DIR'], self.id)
        fullpath = os.path.expanduser(self.home)
        if not os.path.isdir(fullpath):
            os.makedirs(fullpath)

        if send:
            self.send_verification()
        else:
            self.set_verified()

    def send_verification(self):
        send_email_async.delay(
            recipients = [self.email],
            subject = "Index.net.ru :: Account Activation",
            message = """Welcome {0}!

Thank you for registering for an Index.net.ru account.
To activate your account, simply click on the link below or paste this link into the URL field of your favorite browser:

{1}

If you have trouble confirming or accessing your account, please answer this email.

Best regards,
Index.net.ru Team
""".format(self.username, url_for('user_confirm', code=self.verified)))

    def get_verification(self, data):
        double = True
        while double:
            verified = bcrypt.generate_password_hash(data)
            double = User.query.filter_by(verified=verified).first()

        return verified

    def set_verified(self):
        self.verified = ''

    def set_active(self, status = 1):
        self.active = status
