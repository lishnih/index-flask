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
from ..models.logging import Logging


class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        exc = record.__dict__['exc_info']
        trace = traceback.format_exc() if exc else None

        if request:
            path = request.path
            method = request.method
            ip = request.remote_addr

        else:
            path = None
            method = None
            ip = None

        RECORD = Logging(
            user=current_user or None,
            logger=record.__dict__['name'],
            level=record.__dict__['levelname'],
            trace=trace,
            message=record.__dict__['msg'],
            path=path,
            method=method,
            ip=ip,
        )
        db.session.add(RECORD)
        db.session.commit()


db_handler = SQLAlchemyHandler()
db_handler.setLevel(logging.INFO)
app.logger.addHandler(db_handler)

# file_handler = RotatingFileHandler('log.txt')
# file_handler.setLevel(logging.INFO)
# app.logger.addHandler(file_handler)
