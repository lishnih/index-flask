#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-11

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import request, render_template, jsonify, url_for, flash

from flask_login import login_required, current_user

from sqlalchemy.sql import select, text

from ..core.backwardcompat import *
from ..core.db import getDbList, initDb, get_rows_plain
from ..core.obj_helpers import get_query_string, get_query
from ..core.render_response import render_format
from ..core.user_templates import get_user_templates
from ..forms_tables import TableCondForm
from ..models import db, SQLTemplate

from .. import app


### Interface ###

def get_dbs_table(home, db=None):
    dbs_list = getDbList(home)

    names = ['Databases', 'Info']
    dbs_table = [['<a href="{0}"><b><i>{1}</i></b></a>'.format(url_for('views_query', db=dbname), dbname) if db == dbname else
                    '<a href="{0}">{1}</a>'.format(url_for('views_query', db=dbname), dbname),
                  '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=dbname), '>'),
                ] for dbname in dbs_list]

    return names, dbs_table


def views_query_func(db, id):
    format = request.args.get('format')


    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash_t = "База данных не существует: {0}".format(db), 'error'
        return render_format('p/empty.html', format, flash_t)

    sqltemplate = SQLTemplate.query.filter_by(id=id).first()
    if not sqltemplate:
        flash_t = "Запроса не существует: {0}".format(id), 'error'
        return render_format('p/empty.html', format, flash_t)


    sql = sqltemplate.value
    s = select('*').select_from(text("({0})".format(sql))).limit(1)
    try:
        res = session.execute(s)
    except Exception, e:
        flash_t = "Ошибка при выполнении запроса: {0}".format(0), 'error'
        return render_format('p/empty.html', format, flash_t)


    names = res.keys()
    templates_list = [i for i in get_user_templates(current_user)]

    form = TableCondForm(request.form, columns=names, templates_list=templates_list)
    if form.offset.data is None or form.limit.data is None:
        form.offset.data = 0
        form.limit.data = 30

    if request.method == 'POST':
        form.validate()

    criterion = form.get_criterion()
    order = form.get_order()
    offset = form.offset.data
    limit = form.limit.data


    query = get_query(request.form.get('query'))
    if query:
#       db = query.get('db')
#       tables = query.get('tables')
        criterion = query.get('criterion')
        order = query.get('order')


    offset = int(request.form.get('offset', 0))
    limit = int(request.form.get('limit', 30))


    if 'all' in request.args.keys():
        offset = 0
        limit = 0


    if form.template.data and form.template.data <> 'None':
        template_name = 'custom/{0}.html'.format(form.template.data)
        if form.unlim.data == 'on':
            limit = 0
    else:
        template_name = 'db/table.html'


    request_url = request.full_path
    query_str = get_query_string(
                  ver=1,
                  db=db,
                  offset=offset,
                  limit=limit,
                  criterion=criterion,
                  order=order,
                )


    names, rows, total, filtered, shown, page, pages, s = get_rows_plain(
        session, sql, offset, limit, criterion, order)


    if form.template.data and form.template.data <> 'None':
        debug = ''
    else:
        debug = str(s)


    # Выводим
    return render_format(template_name, format,
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
             template = templates_list,
             query_str = query_str,
             debug = debug,
           )


### Routes ###

@app.route('/query/')
@app.route('/query/<db>/')
@login_required
def views_query(db=None):
    names, dbs_table = get_dbs_table(current_user.home, db)
    obj = []

    if db:
        db_uri, session, metadata = initDb(current_user.home, db)
        if not db_uri:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('p/empty.html')

        sqltemplates = SQLTemplate.query.all()

        table_names = ['SQL query', 'Description']
        table_rows = [['<a href="{0}">{1}</a>'.format(url_for('views_query_db_id', db=db, id=sqltemplate.id),
                       sqltemplate.name if sqltemplate.name else "<{0}>".format(sqltemplate.id)),
                       '<a href="{0}">{1}</a>'.format(url_for('views_query_db_dump', db=db, id=sqltemplate.id),
                       sqltemplate.description if sqltemplate.description else '>')
                     ] for sqltemplate in sqltemplates]

        obj.append((table_names, table_rows, db))

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
