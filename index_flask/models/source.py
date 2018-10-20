#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import uuid
from datetime import datetime

from ..app import db
from . import StrType


class Source(db.Model):       # Rev. 2018-09-29
    __tablename__ = 'sources'

    user = db.relationship('User', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    group = db.relationship('Group', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    _group_id = db.Column(db.Integer, db.ForeignKey('groups.id',
        onupdate="CASCADE", ondelete="CASCADE"))

    name = db.Column(db.String, nullable=False, default='')
    uid = db.Column(StrType, nullable=False, default=uuid.uuid4)
    deleted = db.Column(db.Boolean, nullable=False, default=False)

    provider = db.Column(db.String, nullable=False, default='')
    path = db.Column(db.String, nullable=False, default='')
    path_id = db.Column(db.String, nullable=False, default='')
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    db.Index('source_', _user_id, _group_id, name, unique=True)

    def __repr__(self):
        return '<Source {0!r}>'.format(self.name)

    def get_id(self):
        return self.uid

    def get_provider(self):
        if self.provider == 'dropbox-oauth2':
            return "Dropbox"
        elif self.provider == 'google-oauth2':
            return "Google Drive"
        elif self.provider == 'mailru-oauth2':
            return "Mail.Ru Cloud"
        elif self.provider == 'yandex-oauth2':
            return "Yandex Disk"
        else:
            return self.provider
