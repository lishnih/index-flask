#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from ..app import db


class Favorite(db.Model):
    __tablename__ = 'favorites'
    __rev__ = '2019-07-14'

    user = db.relationship('User', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    group = db.relationship('Group', backref=db.backref(__tablename__,
        cascade='all, delete, delete-orphan'))

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    _group_id = db.Column(db.Integer, db.ForeignKey('groups.id',
        onupdate="CASCADE", ondelete="CASCADE"))

    name = db.Column(db.String, nullable=False, server_default='')
    url = db.Column(db.String, nullable=False, server_default='')

    db.Index('favorite_', _user_id, _group_id, name, unique=True)

    def __repr__(self):
        return '<Favorite {0!r}>'.format(self.name)
