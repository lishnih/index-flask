#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os

from flask import ( g, request, render_template, url_for, session,
                    send_from_directory, abort, __version__ )

from flask_login import current_user

from .core.backwardcompat import *
from .core.fileman import list_files
from .core.dump_html import html

from . import app, debug_permission, user_db, get_next


@app.route('/debug/')
def debug():
    if not app.debug or not debug_permission.can():
        abort(404)

    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        output.append([rule.endpoint, methods, url])

    return render_template('debug_debug.html',
             title = 'Url mapping',
             urls = sorted(output),
           )


@app.route('/test/')
@app.route('/test/<path:path>')
def debug_test(path=''):
    if not app.debug or not debug_permission.can():
        abort(404)

    if not path or path[-1] == '/':
        test_url = '/test/{0}'.format(path)
        dirlist, filelist = list_files(test_url, app.root_path)
        return render_template('debug_test.html',
                 title = 'Testing directory',
                 path = test_url,
                 dirlist = dirlist,
                 filelist = filelist,
               )
    else:
        return send_from_directory(os.path.join(app.root_path, 'test'), path)
#       return send_from_directory('test', path)


@app.route('/debug/app')
def debug_app():
    if not app.debug or not debug_permission.can():
        abort(404)

    return html(app)


@app.route('/debug/current_user')
def debug_current_user():
    if not app.debug or not debug_permission.can():
        abort(404)

    return html(current_user)


@app.route('/debug/dbinfo/')
@app.route('/debug/dbinfo/<db>/')
def debug_dbinfo(db=None):
    if not app.debug or not debug_permission.can():
        abort(404)

    if db:
        db_uri, session, metadata, relationships = user_db.get_db(current_user, db)
    else:
        db_uri = session = metadata = relationships = None

    return render_template('debug_dbinfo.html',
             title = 'Databases info',
             dbs_list = user_db.get_dbs_list(current_user),

             db = db,
             db_uri = db_uri,
             session = session,
             metadata = metadata,
             tables = tables,
             relationships = relationships,
             debug = html(metadata),
           )


@app.route('/debug/g')
def debug_g():
    if not app.debug or not debug_permission.can():
        abort(404)

    return html(g)


@app.route('/debug/user_db')
def debug_user_db():
    if not app.debug or not debug_permission.can():
        abort(404)

    return html(user_db.get_data(current_user))


@app.route('/debug/request')
def debug_request():
    if not app.debug or not debug_permission.can():
        abort(404)

    return html(request)


@app.route('/debug/session')
def debug_session():
    if not app.debug or not debug_permission.can():
        abort(404)

    d = {key: val for key, val in session.viewitems()}
    return html((session, d))


@app.route('/debug/ver')
def debug_ver():
    if not app.debug or not debug_permission.can():
        abort(404)

    return __version__
