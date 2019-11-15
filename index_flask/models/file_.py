#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-20

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from ..app import db


class File(db.Model):
    __tablename__ = 'files'
    __bind_key__ = 'indexing'
    __rev__ = '2018-09-27'

    id = db.Column(db.Integer, primary_key=True)
    _source_id = db.Column(db.Integer)

    name = db.Column(db.String, nullable=False, server_default='')
    path = db.Column(db.String, nullable=False, server_default='')
    ext = db.Column(db.String, nullable=False, server_default='')
    size = db.Column(db.Integer, nullable=False, server_default='0')
    modified = db.Column(db.DateTime)
    state = db.Column(db.Integer, nullable=False, server_default='1')

    # Аттрибуты облачных объектов
    path_id = db.Column(db.String, nullable=False, server_default='')
    type = db.Column(db.String, nullable=False, server_default='')
    url = db.Column(db.String, nullable=False, server_default='')
    hash = db.Column(db.String, nullable=False, server_default='')
    md5 = db.Column(db.String, nullable=False, server_default='')
    revision = db.Column(db.String, nullable=False, server_default='')
    preview = db.Column(db.String, nullable=False, server_default='')

    debug = db.Column(db.Text, nullable=False, server_default='')

    def __init__(self, **kargs):
        kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
        db.Model.__init__(self, **kargs_reg)

    def __repr__(self):
        return "<File '{0}' (id:{1})>".format(self.name, self.id)
