#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-21

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import render_template

from flask_login import login_required, current_user

from ..core.backwardcompat import *
from ..core.dump_html import html
from ..core.db import initDb, getDbList
from .. import app


##### Storage #####

global_users_data = {}


##### Interface #####

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
        db_uri, session, metadata = initDb(current_user.home, dbname)
        user_db[dbname] = (db_uri, session, metadata)
    else:
        db_uri, session, metadata = user_db['dbs'][dbname]

    return db_uri, session, metadata


def get_session(current_user, dbname):
    db_uri, session, metadata = get_db(current_user, dbname)

    return session


def get_metadata(current_user, dbname):
    db_uri, session, metadata = get_db(current_user, dbname)

    return metadata


##### Routes #####

@app.route('/user_dbinfo/')
@app.route('/user_dbinfo/<db>/')
@login_required
def ext_user_dbinfo(db=None):
    if db:
        db_uri, session, metadata = user_db.get_db(current_user, db)
    else:
        db_uri = session = metadata = None

    return render_template('ext_user_db/info.html',
             title = 'Databases info',
             dbs_list = get_dbs_list(current_user),

             db = db,
             db_uri = db_uri,
             session = session,
             metadata = metadata,
             debug = html(metadata),
           )


@app.route('/user_db/')
@login_required
def ext_user_db():
    return html(get_data(current_user))
