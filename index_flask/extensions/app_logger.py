#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-27

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import logging
import traceback
# from logging.handlers import RotatingFileHandler

from flask import request
from flask_login import current_user

from ..app import app, db
from ..models.logging_ import Logging


class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        RECORD = Logging(
            _user_id = 0 if current_user.is_anonymous else current_user.id,

            method = request.method if request else None,
            path = request.path if request else None,
            remote_addr = request.remote_addr if request else None,

            levelname = record.__dict__['levelname'],
            msg = record.__dict__['msg'],
            name = record.__dict__['name'],

            trace = traceback.format_exc() if record.__dict__['exc_info'] else None,

            request = request.__dict__,
            referrer = request.referrer,
            args = dict(request.args.items()),
            form = dict(request.form.items()),
            json = request.json,
            data = request.data,

            record = record.__dict__,
        )
        db.session.add(RECORD)
        db.session.commit()


db_handler = SQLAlchemyHandler()
db_handler.setLevel(logging.INFO)
app.logger.addHandler(db_handler)

# file_handler = RotatingFileHandler('log.txt')
# file_handler.setLevel(logging.INFO)
# app.logger.addHandler(file_handler)
