#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-11

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from datetime import datetime

from ..app import db


class Module(db.Model):
    __tablename__ = 'modules'
    __rev__ = '2018-09-14'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    folder = db.Column(db.String, nullable=False, default='views')
    priority = db.Column(db.Integer, nullable=False, default=1)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    loaded = db.Column(db.DateTime, nullable=False, default=datetime(2000, 1, 1))
    error = db.Column(db.String, nullable=False, default='')

    db.Index('module_', name, folder, unique=True)

    def __repr__(self):
        return '<Module {0!r}>'.format(self.name)
