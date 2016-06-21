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


def append_user_to_group(group_name, user):
    group = Group.query.filter_by(name=group_name).first()
    if not group:
        group = Group(group_name)

    user.groups.append(group)


relationship_user_group = db.Table('rs_user_group',
    db.Column('_user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('_group_id', db.Integer, db.ForeignKey('group.id'), nullable=False),
    db.PrimaryKeyConstraint('_user_id', '_group_id'))


class User(db.Model):               # Rev. 2016-06-20
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String)
    company = db.Column(db.String)
    password = db.Column(db.String)
    created = db.Column(db.DateTime)
    token = db.Column(db.String)
    verified = db.Column(db.String)
    active = db.Column(db.Boolean, default=True)
    authenticated = db.Column(db.Boolean, default=True)
#   db.Index('email', email, unique=True)

    home = db.Column(db.String)

    ya_account = db.Column(db.String)
    gd_account = db.Column(db.String)

    ya_token = db.Column(db.String)
    gd_token = db.Column(db.String)

    groups = db.relationship('Group', backref=__tablename__, secondary=relationship_user_group)

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

#   @classmethod
#   def get(cls, id):
#       return cls.user_database.get(id)


class Group(db.Model):              # Rev. 2016-06-20
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    created = db.Column(db.DateTime)

    def __init__(self, name):
        self.name = name
        self.created = datetime.utcnow()


class Database(db.Model):           # Rev. 2016-06-20
    __tablename__ = 'database'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String)
    url = db.Column(db.String)

    def __init__(self, name, user):
        self.name = name
        self._user_id = user.id


db.create_all()
