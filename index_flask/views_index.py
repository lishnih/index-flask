#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import render_template

from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed

from .core.backwardcompat import *
from .core.fileman import list_files
from . import __pkgname__, __description__, __version__

from .a import app


# ===== Roles =====

admin_permission = Permission(RoleNeed('admin'))
debug_permission = Permission(RoleNeed('debug'))
statistics_permission = Permission(RoleNeed('statistics'))


# ===== Routes =====

@app.route("/")
def index():
#   return app.send_static_file('index.html')
    return render_template('p/index.html',
             title = 'Index',
             name = None if current_user.is_anonymous else current_user.name,
             p_admin = admin_permission.can(),
             p_debug = debug_permission.can(),
             p_statistics = statistics_permission.can(),
           )


@app.route("/p/<page>")
def p(page):
    return render_template('p/{0}.html'.format(page),
             name = None if current_user.is_anonymous else current_user.name,
             p_admin = admin_permission.can(),
             p_debug = debug_permission.can(),
             p_statistics = statistics_permission.can(),
           )


@app.route("/about")
def p_about():
    p_admin = admin_permission.can()
    p_debug = debug_permission.can()
    p_statistics = statistics_permission.can()

    additionals = {}
    if p_admin or p_debug:
        import sys
        import flask
        import werkzeug
        import jinja2
        import flask_principal
        import sqlalchemy
        import flask_sqlalchemy
        from flask_login import __about__

        additionals = dict(
            py_version = sys.version,
            flask_version = flask.__version__,
            werkzeug_version = werkzeug.__version__,
            jinja2_version = jinja2.__version__,
            flask_principal_version = flask_principal.__version__,
            flask_login_version = __about__.__version__,
            sqlalchemy_version = sqlalchemy.__version__,
            flask_sqlalchemy_version = flask_sqlalchemy.__version__,
            is_admin = p_admin,
            is_debug = p_debug,
            is_statistics = p_statistics,
        )

    return render_template('p/about.html',
             name = None if current_user.is_anonymous else current_user.name,
             p_admin = p_admin,
             p_debug = p_debug,
             p_statistics = p_statistics,

             pkgname = __pkgname__,
             description = __description__,
             version = __version__,

             **additionals
           )


@app.route('/utils/')
@login_required
def utils():
    utils_path = '/static/utils/'
    dirlist, filelist = list_files(utils_path, app.root_path, '/utils/')

    return render_template('views/views_debug/test.html',
             title = 'Testing directory',
             path = utils_path,
             dirlist = dirlist,
             filelist = filelist,
           )
