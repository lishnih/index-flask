#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-11

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json
from datetime import datetime

from flask import request, render_template, jsonify, redirect, url_for, flash
from jinja2 import Markup, escape

from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed

from sqlalchemy.sql import select, text
from wtforms import Form, StringField, TextAreaField, validators

from ..core.backwardcompat import *
from ..core.db import init_db, get_dbs_list, get_rows_plain
from ..core.render_response import render_format
from ..core.user_templates import get_user_templates
from ..forms_tables import TableCondForm

from ..a import app, db
from ..app import get_next


# ===== Constants =====

limit_default = 15


# ===== Roles =====

admin_permission = Permission(RoleNeed('admin'))


# ===== Models =====

class SQLTemplate(db.Model):  # Rev. 2017-07-23
    __tablename__ = 'sqltemplate'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False, default='')
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, name, value=None, description=''):
        self.name = name
        self.value = value
        self.description = description


db.create_all()


# ===== Forms =====

class NewQueryForm(Form):
    name = StringField('Name *', [
        validators.Length(min=2),
    ])
    value = TextAreaField('Value *', [
        validators.Required(),
    ])
    description = TextAreaField('Description')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        return True


# ===== Interface =====

def get_dbs_table(home, db=None):
    dbs_list = get_dbs_list(home)
    dbs_list = sorted(dbs_list)

    names = ['Databases', 'Info']
    dbs_table = [['<a href="{0}"><b><i>{1}</i></b></a>'.format(url_for('views_query', db=dbname), dbname) if db == dbname else
                    '<a href="{0}">{1}</a>'.format(url_for('views_query', db=dbname), dbname),
                  '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=dbname), '>'),
                ] for dbname in dbs_list]

    return names, dbs_table


def views_query_func(db, id):
    template_name = 'db/table.html'
    templates_list = None
    form = None
    plain = 1
    truncate = 60

    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash_t = "База данных не существует: {0}".format(db), 'error'
        return render_format('p/empty.html', flash_t)

    sqltemplate = SQLTemplate.query.filter_by(id=id).first()
    if not sqltemplate:
        flash_t = "Запроса не существует: {0}".format(id), 'error'
        return render_format('p/empty.html', flash_t)

    sql = sqltemplate.value

    offset = request.values.get('offset', '')
    offset = int(offset) if offset.isdigit() else 0
    limit = request.values.get('limit', '')
    limit = int(limit) if limit.isdigit() else limit_default
    query_json = request.values.get('query_json')

    if query_json:
        query = json.loads(query_json)
#       db = query.get('db')
#       tables = query.get('tables')
        criterion = query.get('criterion')
        mcriterion = criterion
        order = query.get('order')
        morder = order

    else:
        s = select('*').select_from(text("({0})".format(sql))).limit(1)
        try:
            res = session.execute(s)
        except Exception as e:
            flash_t = "Ошибка при выполнении запроса: '{0}'".format(e.message), 'error'
            return render_format('p/empty.html', flash_t)

        names = res.keys()
        templates_list = [i for i in get_user_templates(current_user)]

        form = TableCondForm(request.values, columns=names, templates_list=templates_list)
        form.offset.data = str(offset)
        form.limit.data = str(limit_default)

        if request.method == 'POST':
            form.validate()

        mcriterion, criterion = form.get_criterion()
        morder, order = form.get_order()
#       offset = form.offset.data
#       limit = form.limit.data
        template = form.template.data

        if template and template != 'None':
            template_name = 'custom/{0}.html'.format(template)
            if form.unlim.data == 'on':
                limit = 0
            if form.plain.data == 'off':
                plain = 0

        truncate = int(form.truncate.data) if form.truncate.data.isdigit() else None

    if 'all' in request.args.keys():
        offset = 0
        limit = 0

    names, rows, total, filtered, shown, page, pages, s = get_rows_plain(
        session, sql, offset, limit, mcriterion, morder, plain)

    request_url = request.full_path
    query_json = json.dumps(dict(
                   db = db,
                   sqlid = id,
                   offset = offset,
                   limit = limit,
                   criterion = criterion,
                   order = order,
                 ))

    # Выводим
    return render_format(template_name,
             title = 'Database: {0}'.format(db),
             form = form,
             action = request_url,
             db = db,
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
             templates_list = templates_list,
             truncate = truncate,
             query_json = query_json,
             debug = str(s),
           )


# ===== Routes =====

@app.route('/query/')
@app.route('/query/<db>/')
@login_required
def views_query(db=None):
    names, dbs_table = get_dbs_table(current_user.home, db)
    obj = []

    if db:
        db_uri, session, metadata = init_db(current_user.home, db)
        if not db_uri:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('p/empty.html')

        sqltemplates = SQLTemplate.query.all()
        sqltemplates = sorted(sqltemplates, key=lambda row: row.id)

        table_names = ['SQL query', 'Description']
        table_rows = [[Markup('<a href="{0}">{1}</a>'.format(url_for('views_query_db_id', db=escape(db), id=sqltemplate.id),
                       escape(sqltemplate.name) if sqltemplate.name else "<{0}>".format(sqltemplate.id))),
                       Markup('<a href="{0}">{1}</a>'.format(url_for('views_query_db_dump', db=escape(db), id=sqltemplate.id),
                       escape(sqltemplate.description) if sqltemplate.description else '>'))
                     ] for sqltemplate in sqltemplates]

        obj.append((table_names, table_rows, db, ''))

    return render_template('db/index.html',
             title = 'Databases',
             names = names,
             rows = dbs_table,
             obj = obj,
           )


@app.route('/query/<db>/dump/<id>/')
@login_required
def views_query_db_dump(db, id):
    sqltemplate = SQLTemplate.query.filter_by(id=id).first()
    if not sqltemplate:
        flash("Запроса не существует: {0}".format(id), 'error')
        return render_template('p/empty.html')

    return render_template('p/empty.html',
             text = sqltemplate.value,
    )


@app.route('/query/<db>/<id>', methods=['GET', 'POST'])
@login_required
def views_query_db_id(db, id):
    return views_query_func(db, id)


@app.route('/query_new', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def views_query_new():
    form = NewQueryForm(request.form)
    if request.method == 'POST' and form.validate():
        sqltemplate = SQLTemplate(
            name = form.name.data,
            value = form.value.data,
            description = form.description.data,
        )
        db.session.add(sqltemplate)
        db.session.commit()

        flash('Template added')
        return redirect(get_next('/query/'))

    return render_template('extensions/user_query/newquery.html',
             form = form,
    )
