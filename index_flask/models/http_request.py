#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-13

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import time
import json

from flask import request
from flask_login import current_user

from sqlalchemy.sql import func

from ..app import db
from . import StrType


class HttpRequest(db.Model):
    __tablename__ = 'http_requests'
    __bind_key__ = 'http_requests'
    __rev__ = '2019-12-10'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, nullable=False, server_default='0')

    remote_addr = db.Column(db.String, nullable=False, server_default='')
    url = db.Column(db.String, nullable=False, server_default='')
#   path = db.Column(db.String, nullable=False, server_default='')
    method = db.Column(db.String, nullable=False, server_default='')
    endpoint = db.Column(db.String, nullable=False, server_default='')  # sometimes is None

    status = db.Column(db.Integer, nullable=False, server_default='0')  # response property
    duration = db.Column(db.Float, nullable=False, server_default='0')

    request = db.Column(StrType, nullable=False, server_default='')
    referrer = db.Column(db.String, nullable=False, server_default='')
    args = db.Column(StrType, nullable=False, server_default='')
    form = db.Column(StrType, nullable=False, server_default='')
#   files = db.Column(StrType, nullable=False, server_default='')
    json = db.Column(StrType, nullable=False, server_default='')
    data = db.Column(StrType, nullable=False, server_default='')

    created = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())

    def __init__(self, **kargs):
        self._start = time.time()

        self._user_id = 0 if current_user.is_anonymous else current_user.id

        self.remote_addr = request.remote_addr
        self.url = request.url
        self.method = request.method
        self.endpoint = request.endpoint

#       self.request = request.__dict__
        self.referrer = request.referrer
#       self.args = dict(request.args.items())
#       self.form = dict(request.form.items())
#       self.json = request.json
#       self.data = request.data
