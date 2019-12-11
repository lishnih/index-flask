#!/usr/bin/env python
# coding=utf-8
# Stan 2019-07-06

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from ..app import db
from .user import User


class UserOption(db.Model):
    __tablename__ = 'user_options'
    __rev__ = '2019-07-06'

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
    type = db.Column(db.String, nullable=False, server_default='')
    value = db.Column(db.String, nullable=False, server_default='')

    def __repr__(self):
        return '<UserOption {0!r}>'.format(self.name)


User.options = db.relationship('UserOption', backref=User.__tablename__, lazy='immediate')
