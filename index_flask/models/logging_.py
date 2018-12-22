#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-01

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy.orm import backref, relationship

from ..app import db


class Logging(db.Model):
    __tablename__ = 'logging'
    __bind_key__ = 'logging'
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    __rev__ = '2018-09-27'

    user = relationship('User', backref=backref(__tablename__))

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    logger = db.Column(db.String, nullable=False, server_default='')
    level = db.Column(db.String, nullable=False, server_default='')
    trace = db.Column(db.String, nullable=False, server_default='')
    message = db.Column(db.String, nullable=False, server_default='')
    path = db.Column(db.String, nullable=False, server_default='')
    method = db.Column(db.String, nullable=False, server_default='')
    ip = db.Column(db.String, nullable=False, server_default='')
    created = db.Column(db.DateTime, nullable=False, server_default=func.now())
#   created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
