#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy.sql.expression import true

from flask import url_for

from .. import messages
from ..app import app, db, bcrypt
from ..tools.send_email import send_email


class User(db.Model):
    __tablename__ = 'users'
    __rev__ = '2018-10-21'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False, server_default='')
    company = db.Column(db.String, nullable=False, server_default='')
    password = db.Column(db.String, nullable=False, server_default='-')
    active = db.Column(db.Boolean, nullable=False, server_default=true())
    verified = db.Column(db.String, nullable=False, server_default='-')
    created = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=datetime.utcnow)
    home = db.Column(db.String, nullable=False, server_default='')

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
        send_email(
            message = messages.SEND_VERIFICATION.format(self.username, url_for('user_confirm', code=self.verified)),
            recipients = [self.email, app.config.get('INDEX_REPORT_MAIL')],
            subject = "{} :: Account Activation".format(app.config.get('INDEX_PORTAL_NAME'))
        )

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
