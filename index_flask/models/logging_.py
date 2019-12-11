#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-01

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from sqlalchemy.sql import func

from ..app import db
from . import StrType


class Logging(db.Model):
    __tablename__ = 'logging'
    __bind_key__ = 'logging'
    __rev__ = '2019-12-10'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, nullable=False, server_default='0')

    remote_addr = db.Column(db.String, nullable=False, server_default='')
#   url = db.Column(db.String, nullable=False, server_default='')
    path = db.Column(db.String, nullable=False, server_default='')
    method = db.Column(db.String, nullable=False, server_default='')
    endpoint = db.Column(db.String, nullable=False, server_default='')

#   args = db.Column(db.String, nullable=False, server_default='')
#   asctime = db.Column(db.String, nullable=False, server_default='')
#   created = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
#   exc_info = db.Column(db.String, nullable=False, server_default='')
#   filename = db.Column(db.String, nullable=False, server_default='')
#   funcName = db.Column(db.String, nullable=False, server_default='')
    levelname = db.Column(db.String, nullable=False, server_default='')
#   levelno = db.Column(db.Integer, nullable=False, server_default='0')
#   lineno = db.Column(db.Integer, nullable=False, server_default='0')
#   message = db.Column(db.String, nullable=False, server_default='')
#   module = db.Column(db.String, nullable=False, server_default='')
#   msecs = db.Column(db.Float, nullable=False, server_default='0')
    msg = db.Column(db.String, nullable=False, server_default='')
    name = db.Column(db.String, nullable=False, server_default='')
#   pathname = db.Column(db.String, nullable=False, server_default='')
#   process = db.Column(db.Integer, nullable=False, server_default='0')
#   processName = db.Column(db.String, nullable=False, server_default='')
#   relativeCreated = db.Column(db.Float, nullable=False, server_default='0')
#   stack_info = db.Column(db.String, nullable=False, server_default='')
#   thread = db.Column(db.Integer, nullable=False, server_default='0')
#   threadName = db.Column(db.String, nullable=False, server_default='')

    trace = db.Column(db.String, nullable=False, server_default='')

    request = db.Column(StrType, nullable=False, server_default='')
    referrer = db.Column(db.String, nullable=False, server_default='')
    args = db.Column(StrType, nullable=False, server_default='')
    form = db.Column(StrType, nullable=False, server_default='')
#   files = db.Column(StrType, nullable=False, server_default='')
    json = db.Column(StrType, nullable=False, server_default='')
    data = db.Column(StrType, nullable=False, server_default='')

    record = db.Column(StrType, nullable=False, server_default='')

    created = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
