#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import render_template

from flask_principal import Permission, RoleNeed

from ..app import app
from .. import __pkgname__, __description__, __version__


# ===== Roles =====

admin_permission = Permission(RoleNeed('admin'))
debug_permission = Permission(RoleNeed('debug'))


# ===== Routes =====

@app.route("/")
def index():
#   return app.send_static_file('index.html')
    return render_template('base.html',
        title = 'Index',
        html = 'Welcome to Index system!<br />The portal is under development!',
    )


@app.route("/p/<page>")
def p(page):
    return render_template('p/{0}.html'.format(page))


@app.route("/about")
def about():
    p_admin = admin_permission.can()
    p_debug = debug_permission.can()

    additionals = {}
    if p_admin or p_debug:
        import sys
        import flask
        import werkzeug
        import jinja2
        import wtforms
        import flask_principal
        import flask_bcrypt
        import sqlalchemy
        import flask_sqlalchemy
        import social_core
        import markdown
        import celery
        from flask_login import __about__

        additionals = dict(
            py_version = sys.version,
            flask_version = flask.__version__,
            werkzeug_version = werkzeug.__version__,
            jinja2_version = jinja2.__version__,
            wtforms_version = wtforms.__version__,

            flask_login_version = __about__.__version__,
            flask_principal_version = flask_principal.__version__,
            flask_bcrypt_version = flask_bcrypt.__version__,
            sqlalchemy_version = sqlalchemy.__version__,
            flask_sqlalchemy_version = flask_sqlalchemy.__version__,

            social_core_version = social_core.__version__,
            markdown_version = markdown.version,
            celery_version = celery.__version__,
            version = __version__,
        )

    return render_template('p/about.html',
        pkgname = __pkgname__,
        description = __description__,
        **additionals
    )
