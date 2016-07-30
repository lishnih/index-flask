#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, hashlib, random
from datetime import datetime

from . import db


relationship_user_group = db.Table('rs_user_group',
    db.Column('_user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('_group_id', db.Integer, db.ForeignKey('group.id'), nullable=False),
    db.PrimaryKeyConstraint('_user_id', '_group_id'),
)


class User(db.Model):         # Rev. 2016-06-23
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    company = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    verified = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
#   db.Index('email', email, unique=True)

    home = db.Column(db.String)

    ya_account = db.Column(db.String)
    ya_token = db.Column(db.String)

    gd_account = db.Column(db.String)
    gd_token = db.Column(db.String)

    groups = db.relationship('Group', backref=__tablename__, secondary=relationship_user_group)

    databases = db.relationship('Database', backref=__tablename__, lazy='dynamic')

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    def __init__(self, email, username, name, company, password):
        self.email = email
        self.username = username
        self.name = name
        self.company = company
        self.password = self.get_password(password)
        self.token = self.get_token(email, self.password)
        self.created = datetime.utcnow()

        self.init_env()
        self.run_verification()

    def __repr__(self):
        return '<User {0!r}>'.format(self.name)

    def get_id(self):
        return self.email

    def get_auth_token(self):
        return self.token

    def get_password(self, password):
        return hashlib.sha1(password).hexdigest()

    def get_token(self, email, password):
        rnd = random.randint(0, 100000000000000)
        return hashlib.sha1("{0}_{1}_{2}".format(email, password, rnd)).hexdigest()

    def init_env(self):
        self.home = "C:\\Users\\User\\.config\\index\\{0}".format(self.username)
        if not os.path.isdir(self.home):
            os.makedirs(self.home)

    def run_verification(self):
        self.verified = self.suit_code(self.email)
        self.send_verification()

    def send_verification(self):
        # send verified code
        pass

    def suit_code(self, email):
        double = True
        while double:
            verified = self.get_verification(email)
            double = User.query.filter_by(verified=verified).first()

        return verified

    def get_verification(self, email):
    #   rnd = datetime.now().strftime("%Y%m%d%H%M%S.%f")
        rnd = random.randint(0, 100000000000000)
        return hashlib.md5("{0}_{1}".format(email, rnd)).hexdigest()


class Group(db.Model):        # Rev. 2016-06-29
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime)

    def __init__(self, name, description=''):
        self.name = name.lower()
        self.description = description
        self.created = datetime.utcnow()


class Database(db.Model):     # Rev. 2016-07-12
    __tablename__ = 'database'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    _group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, url, user):
        self._user_id = user.id
        self.name = name
        self.url = url
        self.created = datetime.utcnow()


class Module(db.Model):       # Rev. 2016-07-12
    __tablename__ = 'module'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    folder = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created = db.Column(db.DateTime, nullable=False)
    loaded = db.Column(db.DateTime, nullable=False)
    error = db.Column(db.String, nullable=False, default='')

    db.Index('ext', name, folder, unique=True)

    def __init__(self, name, folder='extensions'):
        self.name = name
        self.folder = folder
        self.created = datetime.utcnow()
        self.loaded = datetime(2000, 1, 1)


db.create_all()
