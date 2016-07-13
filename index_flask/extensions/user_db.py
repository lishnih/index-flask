#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-21

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask_login import login_required, current_user

from ..core.backwardcompat import *
from ..core.dump_html import html
from ..core.db import initDb, getDbList
from .. import app


##### Storage #####

storage = {}


##### Interface #####

def get_data(user):
    if user.is_anonymous:
        return None

    user_db = storage.setdefault(user.id, {
        'dbs': {},
        'dbs_list': getDbList(user.home),
    })

    return user_db


def get_dbs_list(user):
    user_db = get_data(user)
    if not user_db:
        return {}

    return user_db.get('dbs_list', {})


def set_default_db(user, dbname):
    user_db = get_data(user)
    if not user_db:
        return None

    if dbname in user_db.get('dbs_list', {}):
        storage[user.id]['default_db'] = dbname
        return dbname


def get_default_db(user):
    user_db = get_data(user)
    if not user_db:
        return None

    return user_db.get('default_db')


def get_db(user, dbname):
    user_db = get_data(user)
    if not user_db:
        return None, None, None

    if dbname not in user_db.get('dbs', {}):
        db_uri, session, metadata = initDb(user.home, dbname)
        user_db[dbname] = (db_uri, session, metadata)
    else:
        db_uri, session, metadata = user_db['dbs'][dbname]

    return db_uri, session, metadata


def get_session(user, dbname):
    db_uri, session, metadata = get_db(user, dbname)

    return session


def get_metadata(user, dbname):
    db_uri, session, metadata = get_db(user, dbname)

    return metadata


##### Routes #####

@app.route('/user_db/')
@login_required
def ext_user_db():
    return html(get_data(current_user))
