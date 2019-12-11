#!/usr/bin/env python
# coding=utf-8
# Stan 2018-12-21

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from sqlalchemy.sql import func

from ..app import db


class Model(db.Model):
    __tablename__ = 'models'
    __rev__ = '2018-12-21'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    rev = db.Column(db.String, nullable=False, server_default="")
    created = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return '<Model {0!r}>'.format(self.name)
