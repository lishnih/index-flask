#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-21

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from .core.db import initDb, getDbList


global_users_data = {}


def get_data(current_user):
    if current_user.is_anonymous:
        return None

    user_db = global_users_data.setdefault(current_user.id, {
        'dbs': {},
        'dbs_list': getDbList(current_user.home),
    })

    return user_db


def get_dbs_list(current_user):
    user_db = get_data(current_user)
    if not user_db:
        return {}

    return user_db.get('dbs_list', {})


def set_default_db(current_user, dbname):
    user_db = get_data(current_user)
    if not user_db:
        return None

    if dbname in user_db.get('dbs_list', {}):
        global_users_data[current_user.id]['default_db'] = dbname
        return dbname


def get_default_db(current_user):
    user_db = get_data(current_user)
    if not user_db:
        return None

    return user_db.get('default_db')


def get_db(current_user, dbname):
    user_db = get_data(current_user)
    if not user_db:
        return None, None, None, None

    if dbname not in user_db.get('dbs', {}):
        db_uri, session, metadata, relationships = initDb(current_user.home, dbname)
        user_db[dbname] = (db_uri, session, metadata, relationships)
    else:
        db_uri, session, metadata, relationships = user_db['dbs'][dbname]

    return db_uri, session, metadata, relationships


def get_session(current_user, dbname):
    db_uri, session, metadata, relationships = get_db(current_user, dbname)

    return session


def get_metadata(current_user, dbname):
    db_uri, session, metadata, relationships = get_db(current_user, dbname)

    return metadata
