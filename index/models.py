#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import hashlib, random
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from . import app


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String)
    company = db.Column(db.String)
    password = db.Column(db.String)
    created = db.Column(db.DateTime)
    token = db.Column(db.String)
    verified = db.Column(db.String)
#   authenticated = db.Column(db.Boolean, default=False)
#   db.Index('email', email, unique=True)

    databases = db.relationship('Database', backref=__tablename__, lazy='dynamic')

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def __init__(self, email, username, company, password):
        self.email = email
        self.username = username
        self.company = company
        self.password = self.get_password(password)
        self.created = datetime.utcnow()
        self.token = self.get_token(email, self.password)
        self.verified = self.get_verification(email)
        self.send_verification()

    def __repr__(self):
        return '<User {0!r}>'.format(self.username)

    def get_auth_token(self):
        return self.token

    def get_id(self):
        return self.email

    def get_password(self, password):
        return hashlib.sha1(password).hexdigest()

    def get_token(self, email, hpassword):
        randon = random.randint(0, 100000000000000)
        return hashlib.sha1("{0}_{1}_{2}".format(email, hpassword, randon)).hexdigest()

    def get_verification(self, email):
    #   random = datetime.now().strftime("%Y%m%d%H%M%S.%f")
        randon = random.randint(0, 100000000000000)
        return hashlib.md5("{0}_{1}".format(email, randon)).hexdigest()

    def send_verification(self):
        pass

#     @classmethod
#     def get(cls, id):
#         return cls.user_database.get(id)


class Database(db.Model):
    __tablename__ = 'database'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String)
    url = db.Column(db.String)

db.create_all()
