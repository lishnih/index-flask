#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-12

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import uuid
import random

from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false

from ..app import db, bcrypt
from . import StrType
from ..core.json_type import JsonType


relationship_user_app = db.Table('rs_user_app',
    db.Column('_user_id', db.Integer, db.ForeignKey('users.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('_app_id', db.Integer, db.ForeignKey('apps.id',
        onupdate="CASCADE", ondelete="CASCADE")),
#   db.PrimaryKeyConstraint('_user_id', '_app_id'),
)


class RS_App(db.Model):
    __tablename__ = 'rs_user_app'
    __table_args__ = {'extend_existing': True}
    __rev__ = '2016-07-23'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    _app_id = db.Column(db.Integer, db.ForeignKey('apps.id'))

    token = db.Column(db.String, nullable=False, server_default='')
    sticked = db.Column(db.Boolean, nullable=False, server_default=false())
    options = db.Column(db.PickleType, nullable=False, server_default='{}')
    attached = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())

    def __init__(self, **kargs):
        self.token = self.suit_code(self._user_id, self._app_id)

    def get_token(self, user, app):
        rnd = "{0}/{1}/{2}".format(user, app, random.randint(0, 100000000000000))
        return bcrypt.generate_password_hash(rnd)

    def suit_code(self, user, app):
        double = True
        while double:
            token = self.get_token(user, app)
            double = RS_App.query.filter_by(token=token).first()

        return token


class App(db.Model):
    __tablename__ = 'apps'
    __rev__ = '2018-09-29'

    users = db.relationship('User', secondary=relationship_user_app,
        backref=db.backref(__tablename__))

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False, unique=True)
    uid = db.Column(StrType, nullable=False, server_default='', default=uuid.uuid4)
    deleted = db.Column(db.Boolean, nullable=False, server_default=false())

    description = db.Column(db.String, nullable=False, server_default='')
    created = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())

    def __init__(self, name, id=None, description='', **kargs):
        self.id = id
        self.name = name.lower()
        self.description = description

    def __repr__(self):
        return '<App {0!r}>'.format(self.name)

    def get_id(self):
        return self.uid
