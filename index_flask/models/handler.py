#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false

from ..app import db
from . import StrType
from ..core.json_type import JsonType


class Handler(db.Model):
    __tablename__ = 'handlers'
    __table_args__ = (
        UniqueConstraint('_user_id', '_group_id', 'name'),
    )
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

    name = db.Column(db.String, nullable=False, server_default='')
    uid = db.Column(StrType, nullable=False, server_default='', default=uuid.uuid4)
    deleted = db.Column(db.Boolean, nullable=False, server_default=false())

    rev = db.Column(db.String, nullable=False, server_default='')
    module = db.Column(db.String, nullable=False, server_default='')
    entry = db.Column(db.String, nullable=False, server_default='')
    key = db.Column(db.String, nullable=False, server_default='options')
    options = db.Column(JsonType, nullable=False, server_default='{}')
    description = db.Column(db.String, nullable=False, server_default='')
    created = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())

    db.Index('handler_', _user_id, _group_id, name, unique=True)

    def __repr__(self):
        return '<Handler {0!r}>'.format(self.name)

    def get_id(self):
        return self.uid
