#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import uuid
from datetime import datetime

from ..app import db
from . import StrType


class Register(db.Model):
    __tablename__ = 'registers'
    __rev__ = '2018-09-29'

    user = db.relationship('User', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    group = db.relationship('Group', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    _group_id = db.Column(db.Integer, db.ForeignKey('groups.id',
        onupdate="CASCADE", ondelete="CASCADE"))

    section = db.Column(db.String, nullable=False, default='')
    dir = db.Column(db.String, nullable=False, default='')
    name = db.Column(db.String, nullable=False, default='')
    uid = db.Column(StrType, nullable=False, default=uuid.uuid4)
    deleted = db.Column(db.Boolean, nullable=False, default=False)

    value = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    db.Index('register_', _user_id, _group_id, section, dir, name, unique=True)

    def __repr__(self):
        return '<Register {0!r}>'.format(self.name)

    def get_id(self):
        return self.uid
