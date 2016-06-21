#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import Flask, request, jsonify

from flask_login import login_required

from .ext.backwardcompat import *
from . import config, user_data


app = Flask(__name__, static_url_path='')
app.config.from_object(config)
# app.config.from_pyfile('app.cfg')


from . import (
    view_j2,      # j2 package
    views,        # Common views
    views_user,   # User views
    views_debug,  # Debug views
)


@app.route("/j2", methods=["GET", "POST"])
@login_required
def j2():
    return jsonify(view_j2.view_j2(request))
