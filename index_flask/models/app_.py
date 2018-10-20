#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-12

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import uuid
import random
from datetime import datetime

from ..app import db, bcrypt
from . import StrType


relationship_user_app = db.Table('rs_user_app',
    db.Column('_user_id', db.Integer, db.ForeignKey('users.id',
        onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    db.Column('_app_id', db.Integer, db.ForeignKey('apps.id',
        onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    db.PrimaryKeyConstraint('_user_id', '_app_id'),
)


class RS_App(db.Model):       # Rev. 2016-07-23
    __tablename__ = 'rs_user_app'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False, default='')
    sticked = db.Column(db.Boolean, nullable=False, default=True)
    options = db.Column(db.PickleType, nullable=False, default={})
    attached = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self):
        self.token = self.suit_code(self._user_id, self._app_id)

    def get_token(self, user, app):
#       rnd = datetime.now().strftime("%Y%m%d%H%M%S.%f")
        rnd = random.randint(0, 100000000000000)
        return bcrypt.generate_password_hash(rnd)

    def suit_code(self, user, app):
        double = True
        while double:
            token = self.get_token(user, app)
            double = RS_App.query.filter_by(token=token).first()

        return token


class App(db.Model):          # Rev. 2018-09-29
    __tablename__ = 'apps'

    users = db.relationship('User', secondary=relationship_user_app,
        backref=db.backref(__tablename__))

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False, unique=True)
    uid = db.Column(StrType, nullable=False, default=uuid.uuid4)
    deleted = db.Column(db.Boolean, nullable=False, default=False)

    description = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, name, description='', id=None):
        self.name = name.lower()
        self.description = description
        self.id = id

    def __repr__(self):
        return '<App {0!r}>'.format(self.name)

    def get_id(self):
        return self.uid
