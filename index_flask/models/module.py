#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-11

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from sqlalchemy.sql import func
from sqlalchemy.sql.expression import true

from ..app import db


class Module(db.Model):
    __tablename__ = 'modules'
    __rev__ = '2018-09-14'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, server_default='')
    folder = db.Column(db.String, nullable=False, server_default='views')
    priority = db.Column(db.Integer, nullable=False, server_default='1')
    active = db.Column(db.Boolean, nullable=False, server_default=true())
    created = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    loaded = db.Column(db.DateTime(timezone=True), nullable=False, server_default='2000-01-01 12:00:00')
    error = db.Column(db.String, nullable=False, server_default='')

    db.Index('module_', name, folder, unique=True)

    def __repr__(self):
        return '<Module {0!r}>'.format(self.name)
