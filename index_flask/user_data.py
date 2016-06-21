#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-21

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from .ext.db import initDb, getDbList


global_users_data = {}


def get_data(current_user):
    user_data = global_users_data.setdefault(current_user.id, {
        'dbs': {},
        'db_list': getDbList(current_user.home),
    })

    return user_data


def get_db_list(current_user):
    user_data = get_data(current_user)

    return user_data['db_list']


def get_db(current_user, dbname):
    user_data = get_data(current_user)

    if dbname not in user_data['dbs']:
        db_uri, engine, metadata, tables, relationships = initDb(current_user.home, dbname)
        user_data[dbname] = (db_uri, engine, metadata, tables, relationships)
    else:
        db_uri, engine, metadata, tables, relationships = user_data['dbs'][dbname]

    return db_uri, engine, metadata, tables, relationships
