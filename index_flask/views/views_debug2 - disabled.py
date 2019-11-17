#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)


from flask import render_template, abort

from flask_principal import Permission, RoleNeed

from ..app import app
from ..core.dump_html import html


# ===== Roles =====

debug_permission = Permission(RoleNeed('debug'))
# debug_permission = Permission()


# ===== Routes =====

@app.route('/debug/app')
def debug_app():
    if not debug_permission.can():
        abort(404)

    return render_template('base.html',
        without_sidebar = True,
        html = html(app),
    )


@app.route('/debug/jinja')
def debug_jinja():
    if not debug_permission.can():
        abort(404)

    return render_template('base.html',
        without_sidebar = True,
        html = html(app.jinja_env),
    )
