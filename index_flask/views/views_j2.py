#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, jsonify

from flask_login import login_required

from ..app import app
from .. import view_j2


# ===== j2 wrapper for Flask =====

@app.route("/j2", methods=["GET", "POST"])
@login_required
def j2():
    return jsonify(view_j2.view_j2(request))
