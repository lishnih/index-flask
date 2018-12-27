#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-13

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json

from flask import request, render_template
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed

from sqlalchemy import desc, distinct, func, and_, or_, not_
# from sqlalchemy.sql import text

from ..main import app, db
from ..core.db import get_rows_model
from ..core.dump_html import html
from ..forms.dbview import TableCondForm
from ..models.http_request import HttpRequest


# ===== Constants =====

limit_default = 15


# ===== Roles =====

debug_permission = Permission(RoleNeed('debug'))
statistics_permission = Permission(RoleNeed('statistics'))


# ===== Routes =====

@app.route('/requests_g_record')
def requests_g_record():
    if not debug_permission.can():
        abort(404)

    return render_template('base.html',
        without_sidebar = True,
        html = html(g.record),
    )


@app.route('/requests', methods=['GET', 'POST'])
@login_required
@statistics_permission.require(403)
def requests():
    form = None
    plain = 1

    offset = request.values.get('offset', '')
    offset = int(offset) if offset.isdigit() else 0
    limit = request.values.get('limit', '')
    limit = int(limit) if limit.isdigit() else limit_default
    query_json = request.values.get('query_json')

    if query_json:
        query = json.loads(query_json)
        criterion = query.get('criterion')
        mcriterion = criterion
        order = query.get('order')
        morder = order

    else:
        form = TableCondForm(request.form, HttpRequest.__table__, engine=db.engine)
        if form.offset.data is None or form.limit.data is None:
            form.sort_dir1.data = 'DESC'
            form.sorting1.data = 'created'

        form.offset.data = offset
        form.limit.data = limit

        if request.method == 'POST':
            form.validate()

        mcriterion, criterion = form.get_criterion()
        morder, order = form.get_order()
#       offset = form.offset.data
#       limit = form.limit.data
#       template = form.template.data

    if 'all' in request.args.keys():
        offset = 0
        limit = 0

    names, rows, total, filtered, shown, page, pages, s = get_rows_model(
        HttpRequest, offset, limit, mcriterion, morder)

    query_json = json.dumps(dict(
        offset = offset,
        limit = limit,
        criterion = criterion,
        order = order,
    ))

    # Выводим
    return render_template('db/table.html',
        title = 'Request log',
        form = form,
        names = names,
        rows = rows,
        total = total,
        filtered = filtered,
        shown = shown,
        page = page,
        pages = pages,
        colspan = len(names),
        offset = offset,
        limit = limit,
        query_json = query_json,
        debug = str(s),
    )
