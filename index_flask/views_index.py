#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import render_template

from flask_login import current_user
from flask_principal import Permission, RoleNeed

from .core.backwardcompat import *
from .core.dump_html import html

from . import app


admin_permission = Permission(RoleNeed('admin'))
debug_permission = Permission(RoleNeed('debug'))
statistics_permission = Permission(RoleNeed('statistics'))


@app.route("/")
def index():
#   return app.send_static_file('index.html')
    return render_template('index.html',
             title = 'Index',
             name = None if current_user.is_anonymous else current_user.name,
             p_admin = admin_permission.can(),
             p_debug = debug_permission.can(),
             p_statistics = statistics_permission.can(),
           )
