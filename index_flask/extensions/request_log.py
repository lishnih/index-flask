#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-13

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import time, math

from flask import g, request, render_template, redirect, flash
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed

from sqlalchemy import desc, distinct, func, and_, or_, not_
from wtforms import Form, StringField, IntegerField, SelectField, validators

from ..core.backwardcompat import *
from ..core.dump_html import html
from ..models import db
from .. import app


##### Role #####

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


##### Form #####

class TableCondForm(Form):
    offset = IntegerField('Offset')
    limit = IntegerField('Limit')

    column1 = SelectField('Filter')
    column2 = SelectField('Filter')
    column3 = SelectField('Filter')

    conditions = [[i,i] for i in [
        '', '=', '!=', '~', '!~', '>', '>=', '<', '<=',
        'consist', 'in', 'not in', 'between', 'not between',
        'is None', 'not is None', 'is empty', 'not is empty'
    ]]
    condition1 = SelectField('Filter', choices=conditions)
    condition2 = SelectField('Filter', choices=conditions)
    condition3 = SelectField('Filter', choices=conditions)

    value1 = StringField('Filter')
    value2 = StringField('Filter')
    value3 = StringField('Filter')

    sort_dirs = [[i,i] for i in ['ASC', 'DESC']]
    sort_dir1 = SelectField('Filter', choices=sort_dirs)
    sort_dir2 = SelectField('Filter', choices=sort_dirs)
    sort_dir3 = SelectField('Filter', choices=sort_dirs)

    sorting1 = SelectField('Sorting')
    sorting2 = SelectField('Sorting')
    sorting3 = SelectField('Sorting')

    def __init__(self, form, names, **kwargs):
        super(TableCondForm, self).__init__(form, **kwargs)

        names = names[:]
        names.insert(0, '')
        fields = [[i,i] for i in names]

        self.column1.choices = fields
        self.column2.choices = fields
        self.column3.choices = fields

        self.sorting1.choices = fields
        self.sorting2.choices = fields
        self.sorting3.choices = fields

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        return True

    def get_criterion(self):
        criterion = []
        if self.column1.data:
            clause = get_clause(RequestRecord, self.column1.data, [self.condition1.data, self.value1.data])
            if clause is not None:
                criterion.append(clause)
        if self.column2.data:
            clause = get_clause(RequestRecord, self.column2.data, [self.condition2.data, self.value2.data])
            if clause is not None:
                criterion.append(clause)
        if self.column3.data:
            clause = get_clause(RequestRecord, self.column3.data, [self.condition3.data, self.value3.data])
            if clause is not None:
                criterion.append(clause)

        return criterion

    def get_order(self):
        order = []
        if self.sorting1.data:
            sort_column = get_order(RequestRecord, self.sorting1.data, self.sort_dir1.data)
            if sort_column is not None:
                order.append(sort_column)
        if self.sorting2.data:
            sort_column = get_order(RequestRecord, self.sorting2.data, self.sort_dir2.data)
            if sort_column is not None:
                order.append(sort_column)
        if self.sorting3.data:
            sort_column = get_order(RequestRecord, self.sorting3.data, self.sort_dir3.data)
            if sort_column is not None:
                order.append(sort_column)

        return order


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


def get_clause(model, column, value):
    column = model.__table__.c.get(column)
    if column is None:
        return

    clause = None
    if value is None:
        clause = column == None
    elif isinstance(value, basestring) or isinstance(value, int):
        clause = column == value
    elif isinstance(value, float):
        clause = column.like(value)
    else:
#         '', '=', '!=', '~', '!~', '>', '>=', '<', '<=',
#         'consist', 'in', 'not in', 'between', 'not between',
#         'is None', 'not is None', 'is empty', 'not is empty'

        condition, value = value
        if condition == '=' or condition == '==':
            clause = column == value
        elif condition == '!=':
            clause = column != value
        elif condition == '~':
            clause = column.like(value)
        elif condition == '!~':
            clause = not_(column.like(value))
        elif condition == '>':
            clause = column > value
        elif condition == '>=':
            clause = column >= value
        elif condition == '<':
            clause = column < value
        elif condition == '<=':
            clause = column <= value
        elif condition == 'consist':
            clause = column.like("%{0}%".format(value))

    return clause


def get_order(model, column, cond):
    column = model.__table__.c.get(column)
    if column is None:
        return

    return desc(column) if cond == 'DESC' else column


##### Routes #####

@app.route('/request_log', methods=['GET', 'POST'])
@login_required
@statistics_permission.require(403)
def ext_request_log():
    names = [i.name for i in RequestRecord.__table__.c]

    form = TableCondForm(request.form, names)
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
    s = s.order_by(*order).offset(offset).limit(limit)
    showed = s.count()

    records = s.all()
    rows = [[record.__dict__.get(i) for i in names] for record in records]

    pages = int(math.ceil(filtered / limit)) if limit else 0
    page = int(math.floor(offset / limit)) + 1 if limit else 0
    if page > pages: page = 0

    return render_template('table.html',
             form = form,
             names = names,
             rows = rows,
             total = total,
             filtered = filtered,
             showed = showed,
             page = page,
             pages = pages,
             debug = str(s),
           )
