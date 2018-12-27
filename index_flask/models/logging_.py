#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-01

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from sqlalchemy.sql import func

from ..app import db


class Logging(db.Model):
    __tablename__ = 'logging'
    __bind_key__ = 'logging'
    __rev__ = '2018-09-27'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, nullable=False, server_default='0')

    logger = db.Column(db.String, nullable=False, server_default='')
    level = db.Column(db.String, nullable=False, server_default='')
    trace = db.Column(db.String, nullable=False, server_default='')
    message = db.Column(db.String, nullable=False, server_default='')
    path = db.Column(db.String, nullable=False, server_default='')
    method = db.Column(db.String, nullable=False, server_default='')
    ip = db.Column(db.String, nullable=False, server_default='')
    created = db.Column(db.DateTime, nullable=False, server_default=func.now())
