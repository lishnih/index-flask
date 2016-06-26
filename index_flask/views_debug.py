#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os

from flask import ( g, request, render_template, url_for, session,
                    send_from_directory, abort, __version__ )

from flask_login import login_required, current_user

from .ext.backwardcompat import *
from .ext.fileman import list_files
from .ext.dump_html import html

from . import app, user_data


@app.route('/current_user')
@login_required
def debug_current_user():
    if not app.debug:
        abort(404)

    return html(current_user)


@app.route('/user_data')
@login_required
def debug_global_object():
    if not app.debug:
        abort(404)

    return html(user_data.get_data(current_user))


@app.route('/dbinfo/')
@app.route('/dbinfo/<db>/')
@login_required
def debug_dbinfo(db=None):
    if not app.debug:
        abort(404)

    if db:
        db_uri, session, metadata, relationships = user_data.get_db(current_user, db)
    else:
        db_uri = session = metadata = relationships = None

    return render_template('debug_dbinfo.html',
             title = 'Databases info',
             dbs_list = user_data.get_dbs_list(current_user),

             db = db,
             db_uri = db_uri,
             session = session,
             metadata = metadata,
             tables = tables,
             relationships = relationships,
             debug = html(metadata),
           )


@app.route('/debug')
@login_required
def debug_debug():
    if not app.debug:
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
@login_required
def debug_test(path=''):
    if not app.debug:
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


# @app.route('/user/')
# @login_required
# def debug_user():
#     user_url = '/{0}/user/'.format(app.template_folder)
#     dirlist, filelist = list_files(user_url, app.root_path, '/user/')
#     return render_template('debug_test.html',
#              title = 'User templates directory',
#              path = '/user/',
#              dirlist = dirlist,
#              filelist = filelist,
#            )
#
#
# @app.route('/user/<path:path>')
# @login_required
# def debug_user_path(path=''):
#     user_html = 'user/{0}'.format(path)
#     return render_template(user_html,
#              title = 'User',
#            )


@app.route('/ver')
@login_required
def debug_ver():
    if not app.debug:
        abort(404)

    return __version__


@app.route('/app')
@login_required
def debug_app():
    if not app.debug:
        abort(404)

    return html(app)


@app.route('/session')
@login_required
def debug_session():
    if not app.debug:
        abort(404)

    d = {key: val for key, val in session.viewitems()}
    return html((session, d))


@app.route('/request')
@login_required
def debug_request():
    if not app.debug:
        abort(404)

    return html(request)


@app.route('/g')
@login_required
def debug_g():
    if not app.debug:
        abort(404)

    return html(g)
