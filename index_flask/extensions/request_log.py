#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-13

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import time, json

from flask import g, request, render_template, g
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed

from sqlalchemy import desc, distinct, func, and_, or_, not_
from sqlalchemy.types import TypeDecorator, Integer, Float
# from sqlalchemy.sql import text
from wtforms import Form, StringField, IntegerField, SelectField, validators

from ..core.backwardcompat import *
from ..core.db import get_rows_model
from ..core.render_response import render_format
from ..core.dump_html import html
from ..forms_tables import TableCondForm

from ..a import app, db


### Constants ###

limit_default = 15


##### Roles #####

debug_permission = Permission(RoleNeed('debug'))
statistics_permission = Permission(RoleNeed('statistics'))


##### Models #####

class EpochTime(TypeDecorator):
    impl = Integer

    def process_bind_param(self, value, dialect):
        if isinstance(value, string_types):
            if value.isdigit():
                return value

            if len(value) == 10:
                value = time.mktime(time.strptime(value, "%Y-%m-%d"))
            elif len(value) == 13:
                value = time.mktime(time.strptime(value, "%Y-%m-%d %H"))
            elif len(value) == 16:
                value = time.mktime(time.strptime(value, "%Y-%m-%d %H:%M"))

        return value

    def process_result_value(self, value, dialect):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))


class RequestRecord(db.Model):  # Rev. 2016-07-21
    __tablename__ = 'request_record'

    id = db.Column(db.Integer, primary_key=True)
    remote_addr = db.Column(db.String)  # request property
    url = db.Column(db.String)          # request property
    method = db.Column(db.String)       # request property
    endpoint = db.Column(db.String)     # request property, sometimes is None
    user = db.Column(db.Integer, nullable=False)
    start = db.Column(EpochTime, nullable=False)
    duration = db.Column(db.Float)
    status = db.Column(db.Integer)      # response property
    values = db.Column(db.Text, nullable=False)

    def __init__(self):
        self.remote_addr = request.remote_addr
        self.url = request.url
        self.method = request.method
        self.endpoint = request.endpoint
        self.user = 0 if current_user.is_anonymous else current_user.id
        self._start = time.time()
        self.start = self._start
        self.values = json.dumps(dict(request.values.items()))

db.create_all()


##### Interface #####

@app.before_request
def before_request():
    if request.endpoint not in ['static', 'user_register',
            'user_login', 'user_change_password']:
        g.record = RequestRecord()
        db.session.add(g.record)
        db.session.commit()


@app.after_request
def after_request(response):
    if 'record' in g:
        g.record.duration = time.time() - g.record._start
        g.record.status = response.status_code
        db.session.commit()

    return response


def views_request_func():
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
        form = TableCondForm(request.form, RequestRecord.__table__, engine=db.engine)
        if form.offset.data is None or form.limit.data is None:
            form.sort_dir1.data = 'DESC'
            form.sorting1.data = 'start'

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
        RequestRecord, offset, limit, mcriterion, morder)


    request_url = request.full_path
    query_json = json.dumps(dict(
                   offset = offset,
                   limit = limit,
                   criterion = criterion,
                   order = order,
                 ))


    # Выводим
    return render_format('db/table.html',
             title = 'Request log',
             form = form,
             action = request_url,
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
#            templates_list = templates_list,
             query_json = query_json,
             debug = str(s),
           )


##### Routes #####

@app.route('/debug/request_log')
def debug_request_log():
    if not debug_permission.can():
        abort(404)

    return html(g.record)


@app.route('/request_log', methods=['GET', 'POST'])
@login_required
@statistics_permission.require(403)
def ext_request_log():
    return views_request_func()
