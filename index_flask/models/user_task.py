#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import uuid

from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false

from ..app import db
from . import StrType
from ..core.json_type import JsonType


class UserTask(db.Model):
    __tablename__ = 'user_tasks'
    __rev__ = '2019-01-19'

    user = db.relationship('User', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    group = db.relationship('Group', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    source = db.relationship('Source', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    handler = db.relationship('Handler', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    _group_id = db.Column(db.Integer, db.ForeignKey('groups.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    _source_id = db.Column(db.Integer, db.ForeignKey('sources.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    _handler_id = db.Column(db.Integer, db.ForeignKey('handlers.id',
        onupdate="CASCADE", ondelete="CASCADE"))

    name = db.Column(db.String, nullable=False, server_default='')
    uid = db.Column(StrType, nullable=False, server_default='', default=uuid.uuid4)
    deleted = db.Column(db.Boolean, nullable=False, server_default=false())

    type = db.Column(db.Integer, nullable=False, server_default='1')
    mode = db.Column(db.String, nullable=False, server_default='manual')
    options = db.Column(JsonType, nullable=False, server_default='{}', default={})
    command = db.Column(db.String, nullable=False, server_default='')
    pid = db.Column(db.Integer, nullable=False, server_default='0')
    status = db.Column(db.Integer, nullable=False, server_default='0')
    send_when_finished = db.Column(db.Boolean, nullable=False, server_default=false())
    created = db.Column(db.DateTime, nullable=False, server_default=func.now())
    finished = db.Column(db.DateTime)

    next = db.Column(db.Integer, nullable=False, server_default='0')
    next_uid = db.Column(db.String, nullable=False, server_default='')

#   db.Index('user_task_', _user_id, _group_id, _source_id, _handler_id, \
#       name, unique=True)

    def __repr__(self):
        return '<UserTask {0!r}>'.format(self.name)

    def get_id(self):
        return self.uid
