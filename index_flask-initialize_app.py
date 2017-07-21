#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-20

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from index_flask.a import app, db
from index_flask.models import User, Group


def init_admin():
    user_id = 1

    user = User.query.filter_by(id=user_id).first()
    if not user:
        user = User(
            email    = 'root@localhost',
            username = 'root',
            name     = 'root',
            company  = '',
            password = '1234',
        )
        db.session.add(user)

    group_name = 'admin'
    group = Group.query.filter_by(name=group_name).first()
    if not group:
        group = Group(group_name)

    user.groups.append(group)

    group_name = 'debug'
    group = Group.query.filter_by(name=group_name).first()
    if not group:
        group = Group(group_name)

    user.groups.append(group)

    group_name = 'statistics'
    group = Group.query.filter_by(name=group_name).first()
    if not group:
        group = Group(group_name)

    user.groups.append(group)

    db.session.commit()


if __name__ == '__main__':
    init_admin()
