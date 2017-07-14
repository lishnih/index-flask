#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-26

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import request, render_template, jsonify, url_for, flash

from flask_login import login_required, current_user

from sqlalchemy.sql import select

from ..core.backwardcompat import *
from ..core.db import getDbList, initDb, get_rows_base, get_rows_ext
from ..core.obj_helpers import get_query_string, get_query
from ..core.render_response import render_format
from ..core.user_templates import get_user_templates
from ..core.dump_html import html
from ..forms_tables import TableCondForm

from .. import app


### Interface ###

def get_dbs_table(home, db=None):
    dbs_list = getDbList(home)

    names = ['Databases', 'Info', 'Session', 'Metadata']
    dbs_table = [['<a href="{0}"><b><i>{1}</i></b></a>'.format(url_for('views_db', db=dbname), dbname) if db == dbname else
                    '<a href="{0}">{1}</a>'.format(url_for('views_db', db=dbname), dbname),
                  '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=dbname), '>'),
                  '<a href="{0}">{1}</a>'.format(url_for('views_db_session', db=dbname), '>'),
                  '<a href="{0}">{1}</a>'.format(url_for('views_db_metadata', db=dbname), '>'),
                ] for dbname in dbs_list]

    return names, dbs_table


def views_db_func(db, tables):
    format = request.args.get('format')


    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash_t = "База данных не существует: {0}".format(db), 'error'
        return render_format('p/empty.html', format, flash_t)


    mtables = [metadata.tables.get(i) for i in tables.split('|')]
    mtables = [i for i in mtables if i is not None]

    if not len(mtables):
        flash_t("Проверьте таблицы: {0}".format(tables), 'error')
        return render_format('p/empty.html', format, flash_t)


    templates_list = [i for i in get_user_templates(current_user)]

    form = TableCondForm(request.form, mtables, templates_list=templates_list)
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
                  ver = 1,
                  db = db,
                  tables = tables,
                  offset = offset,
                  limit = limit,
                  criterion = criterion,
                  order = order,
                )


    names, rows, total, filtered, shown, page, pages, s = get_rows_ext(
        session, mtables, offset, limit, criterion, order)


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

@app.route('/db/')
@app.route('/db/<db>/', methods=["GET", "POST"])
@login_required
def views_db(db=None):
    names, dbs_table = get_dbs_table(current_user.home, db)
    obj = []

    if db:
        tables = request.args.get('tables')
        if tables:
            return views_db_func(db, tables)


        db_uri, session, metadata = initDb(current_user.home, db)
        if not db_uri:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('p/empty.html')


        table_names = ['Tables', 'w/options']
        table_rows = [['<a href="{0}">{1}</a>'.format(url_for('views_db_table', db=db, table=table), table),
                       '<a href="{0}">{1}</a>'.format(url_for('views_db', db=db, tables=table), table)
                     ] for table in metadata.tables.keys()]

        obj.append((table_names, table_rows, db))

    return render_template('db/index.html',
             title = 'Databases',
             names = names,
             rows = dbs_table,
             obj = obj,
           )


@app.route('/db/session/<db>/')
@login_required
def views_db_session(db):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    return html(session)


@app.route('/db/metadata/<db>/')
@login_required
def views_db_metadata(db):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    return html(metadata)


@app.route('/db/info/<db>')
@login_required
def views_db_info(db):
    names, dbs_table = get_dbs_table(current_user.home, db)
    obj = []

    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    table_names = ['Column', 'type', 'primary_key', 'nullable', 'index', 'autoincrement', 'unique', 'default', 'foreign_keys', 'onupdate']
    for table, mtable in metadata.tables.items():
        table_rows = []
        for c in mtable.c:
            table_rows.append(['<a href="{0}">{1}</a>'.format(url_for('views_db_table_column_distinct', db=db, table=table, column=c.name), c.name),
                               '<a href="{0}">{1}</a>'.format(url_for('views_db_table_column_info', db=db, table=table, column=c.name), repr(c.type)),
                               c.primary_key, c.nullable, c.index, c.autoincrement, c.unique, c.default, c.foreign_keys, c.onupdate])

        table = '<a href="{0}">{1}</a>'.format(url_for('views_db_table_info', db=db, table=table), table)
        obj.append((table_names, table_rows, table))

    return render_template('db/index.html',
             title = 'Database Info',
             names = names,
             rows = dbs_table,
             obj = obj,
           )


@app.route('/db/info/<db>/<table>')
@login_required
def views_db_table_info(db, table):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    mtable = metadata.tables.get(table)
    if mtable is None:
        flash("Таблицы не существует: {0}".format(table), 'error')
        return render_template('p/empty.html')

    return html(mtable)


@app.route('/db/info/<db>/<table>/<column>')
@login_required
def views_db_table_column_info(db, table, column):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    mtable = metadata.tables.get(table)
    if mtable is None:
        flash("Таблицы не существует: {0}".format(table), 'error')
        return render_template('p/empty.html')

    mcolumn = mtable.c.get(column)
    if mcolumn is None:
        flash("Колонки не существует: {0}".format(column), 'error')
        return render_template('p/empty.html')

    return html(mcolumn)


@app.route('/db/distinct/<db>/<table>/<column>')
@login_required
def views_db_table_column_distinct(db, table, column):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    mtable = metadata.tables.get(table)
    if mtable is None:
        flash("Таблицы не существует: {0}".format(table), 'error')
        return render_template('p/empty.html')

    mcolumn = mtable.c.get(column)
    if mcolumn is None:
        flash("Колонки не существует: {0}".format(column), 'error')
        return render_template('p/empty.html')

    names = ['Values']
    s = select([mcolumn.distinct()]).select_from(mtable).order_by(mcolumn)
    res = session.execute(s)
    rows = [[i[0]] for i in res.fetchall()]

    return render_template('dump_table.html',
             names = names,
             rows = rows,
             total = len(rows),
           )


@app.route('/db/<db>/<table>/', methods=["GET", "POST"])
@login_required
def views_db_table(db, table):
    format = request.args.get('format')


    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash_t = "База данных не существует: {0}".format(db), 'error'
        return render_format('p/empty.html', format, flash_t)

    mtable = metadata.tables.get(table)
    if mtable is None:
        flash_t = "Таблица не существует: {0}".format(table), 'error'
        return render_format('p/empty.html', format, flash_t)


    offset = int(request.form.get('offset', 0))
    limit = int(request.form.get('limit', 30))

    if 'all' in request.args.keys():
        offset = 0
        limit = 0


    names, rows, total, filtered, shown, page, pages, s = get_rows_base(session, mtable, offset, limit)


    # Выводим
    return render_format('db/table.html', format,
             title = 'Database: {0}'.format(db),
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
             debug = str(s),
           )
