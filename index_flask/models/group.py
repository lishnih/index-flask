#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false

from ..app import db


relationship_user_group = db.Table('rs_user_group',   # Rev. 2018-09-14
    db.Column('_user_id', db.Integer, db.ForeignKey('users.id',
        onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    db.Column('_group_id', db.Integer, db.ForeignKey('groups.id',
        onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    db.Column('manage', db.Boolean, nullable=False, server_default=false()),
    db.PrimaryKeyConstraint('_user_id', '_group_id'),
)


class Group(db.Model):
    __tablename__ = 'groups'
    __rev__ = '2018-09-14'

    users = db.relationship('User', secondary=relationship_user_group,
        backref=db.backref(__tablename__))

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False, server_default='')
    created = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())

    def __init__(self, name, description='', **kargs):
        self.name = name.lower()
        self.description = description

    def __repr__(self):
        return '<Group {0!r}>'.format(self.name)

    def get_id(self):
        return self.name
