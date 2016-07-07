#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import render_template

from flask_login import current_user

from .core.backwardcompat import *
from .core.dump_html import html

from . import app, admin_permission


@app.route("/")
def index():
#   return app.send_static_file('index.html')

    name = None if current_user.is_anonymous else current_user.name
    admin = admin_permission.can()
    return render_template('index.html',
             title = 'Index',
             name = name,
             admin = admin,
           )
