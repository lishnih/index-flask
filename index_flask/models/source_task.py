#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import uuid
from datetime import datetime

from ..app import db
from . import StrType
from ..core.json_type import JsonType
from .handler import Handler
from .source import Source


class SourceTask(db.Model):
    __tablename__ = 'source_tasks'
    __rev__ = '2018-11-20'

    source = db.relationship('Source', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    handler = db.relationship('Handler', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))

    id = db.Column(db.Integer, primary_key=True)
    _source_id = db.Column(db.Integer, db.ForeignKey('sources.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    _handler_id = db.Column(db.Integer, db.ForeignKey('handlers.id',
        onupdate="CASCADE", ondelete="CASCADE"))

    name = db.Column(db.String, nullable=False, default='')
    uid = db.Column(StrType, nullable=False, default=uuid.uuid4)
    deleted = db.Column(db.Boolean, nullable=False, default=False)

    mode = db.Column(db.String, nullable=False, default='manual')
    options = db.Column(JsonType, nullable=False, default={})
    status = db.Column(db.Integer, nullable=False, default=0)
    pid = db.Column(db.Integer, nullable=False, default=0)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    finished = db.Column(db.DateTime)

    db.Index('source_task_', _source_id, _handler_id, name, unique=True)

    def __repr__(self):
        return '<SourceTask {0!r}>'.format(self.name)

    def get_id(self):
        return self.uid
