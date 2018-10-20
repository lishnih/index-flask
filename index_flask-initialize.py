#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-20

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from sqlalchemy import and_


# ===== Create INDEX_SQLITE_HOME directory =====
from index_flask.config import *

print('INDEX_SQLITE_HOME:', INDEX_SQLITE_HOME)
if not os.path.isdir(INDEX_SQLITE_HOME):
    os.mkdir(INDEX_SQLITE_HOME)


# ===== Import =====
from index_flask.app import db
from index_flask.models.user import User
from index_flask.models.group import Group, relationship_user_group
from index_flask.models.handler import Handler


# ===== Functions =====
def append_to_group(user, group_name, manage=False):
    group = Group.query.filter_by(name=group_name).first()
    if not group:
        group = Group(group_name)

    if user not in group.users:
        user.groups.append(group)
        db.session.commit()

    if manage:
        s = relationship_user_group.update(values=dict(
              manage = manage,
            )).where(
              and_(
                relationship_user_group.c._user_id == user.id,
                relationship_user_group.c._group_id == group.id,
              )
            )
        res = db.session.execute(s)


def init_admin():
    user_id = 1

    user = User.query.filter_by(id=user_id).first()
    if not user:
        user = User(
            username = 'root',
            email = 'root@localhost',
            password = '1234',
            name = 'root',
            id = user_id,
        )
        db.session.add(user)
        user.init_env(send=False)

    append_to_group(user, 'admin', True)
    append_to_group(user, 'debug', True)
    append_to_group(user, 'statistics', True)
    append_to_group(user, 'premium', True)
    append_to_group(user, 'testing', True)
    append_to_group(user, 'beta', True)


def init_user():
    user_id = 1001

    user = User.query.filter_by(id=user_id).first()
    if not user:
        user = User(
            username = 'user',
            email = 'user@localhost',
            password = '1234',
            name = 'user',
            id = user_id,
        )
        db.session.add(user)
        user.init_env(send=False)

    append_to_group(user, 'debug')
    append_to_group(user, 'statistics')
    append_to_group(user, 'testing')


if __name__ == '__main__':
    db.create_all()
    init_admin()
    init_user()
    db.session.commit()

    if not Handler.query.filter_by(name='initial_scan').first():
        handler = Handler(name='initial_scan', module='index_flask.handlers.initial_scan', entry='proceed')
        db.session.add(handler)
    db.session.commit()
