#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-13

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import time, math

from flask import g, request, render_template
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed

from sqlalchemy import desc, distinct, func, and_, or_, not_
from wtforms import Form, StringField, IntegerField, SelectField, validators

from ..core.backwardcompat import *
from ..core.dump_html import html
from ..forms_tables import TableCondForm
from ..models import db

from .. import app


##### Role #####

debug_permission = Permission(RoleNeed('debug'))
statistics_permission = Permission(RoleNeed('statistics'))


##### Model #####

class RequestRecord(db.Model):  # Rev. 2016-07-13
    __tablename__ = 'request_record'

    id = db.Column(db.Integer, primary_key=True)
    remote_addr = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    endpoint = db.Column(db.String)
    user = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Integer)

    def __init__(self):
        self.remote_addr = request.remote_addr
        self.url = request.url
        self.endpoint = request.endpoint
        self.user = 0 if current_user.is_anonymous else current_user.id
        self.start = time.time()
#       self.start = datetime.utcnow()

db.create_all()


##### Interface #####

@app.before_request
def before_request():
    if request.endpoint not in ['static', 'debug_test']:
        g.record = RequestRecord()
        db.session.add(g.record)
        db.session.commit()

@app.after_request
def after_request(response):
    if 'record' in g:
        g.record.duration = time.time() - g.record.start
        g.record.status = response.status_code
        db.session.commit()
    return response


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
    form = TableCondForm(request.form, RequestRecord.__table__)
    if form.offset.data is None or form.limit.data is None:
        form.offset.data = 0
        form.limit.data = 100
        form.sort_dir1.data = 'DESC'
        form.sorting1.data = 'start'

    if request.method == 'POST':
        form.validate()

    criterion = form.get_criterion()
    order = form.get_order()
    offset = form.offset.data
    limit = form.limit.data

    s = RequestRecord.query
    total = s.count()
    s = s.filter(*criterion)
    filtered = s.count()
    if offset > filtered:
        offset = 0
    s = s.order_by(*order).offset(offset).limit(limit)
    shown = s.count()

    records = s.all()
    names = [i.name for i in RequestRecord.__table__.c]
    rows = [[record.__dict__.get(i) for i in names] for record in records]

    pages = int(math.ceil(filtered / limit)) if limit else 0
    page = int(math.floor(offset / limit)) + 1 if limit else 0
    if page > pages: page = 0

    return render_template('db/table.html',
             form = form,
             names = names,
             rows = rows,
             total = total,
             filtered = filtered,
             shown = shown,
             page = page,
             pages = pages,
             debug = str(s),
           )
