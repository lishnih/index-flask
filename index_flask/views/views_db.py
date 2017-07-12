#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-26

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import request, render_template, jsonify, url_for, flash

from flask_login import login_required, current_user

from sqlalchemy.sql import select

from ..core.backwardcompat import *
from ..core.db import getDbList, initDb, get_rows_base
from ..core.dump_html import html

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


### Routes ###

@app.route('/db/')
@app.route('/db/<db>/')
@login_required
def views_db(db=None):
    names, dbs_table = get_dbs_table(current_user.home, db)
    obj = []

    if db:
        db_uri, session, metadata = initDb(current_user.home, db)
        if not db_uri:
            flash("Базы данных не существует: {0}".format(db), 'error')
            return render_template('p/empty.html')

        table_names = ['Tables']
        table_rows = [['<a href="{0}">{1}</a>'.format(url_for('views_db_table', db=db, table=table), table),
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
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    return html(session)


@app.route('/db/metadata/<db>/')
@login_required
def views_db_metadata(db):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    return html(metadata)


@app.route('/db/info/<db>')
@login_required
def views_db_info(db):
    names, dbs_table = get_dbs_table(current_user.home, db)
    obj = []

    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
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
        flash("Базы данных не существует: {0}".format(db), 'error')
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
        flash("Базы данных не существует: {0}".format(db), 'error')
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
        flash("Базы данных не существует: {0}".format(db), 'error')
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
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    mtable = metadata.tables.get(table)
    if mtable is None:
        flash("Таблицы не существует: {0}".format(table), 'error')
        return render_template('p/empty.html')

    offset = int(request.form.get('offset', 0))
    limit = int(request.form.get('limit', 100))

    if 'all' in request.args.keys():
        offset = 0
        limit = 0

    names, rows, total, filtered, showed, page, pages, s = get_rows_base(session, mtable, offset, limit)

    # Выводим
    if request.method == 'POST':
        return jsonify(
                 full_rows_count = total,
                 filtered_rows_count = filtered,
                 rows_count = showed,
                 offset = offset,
                 limit = limit,
                 rows = rows,
               )
    else:
        return render_template('db/table.html',
                 title = 'Database: {0}'.format(db),
                 db = db,
                 full_rows_count = total,
                 filtered_rows_count = filtered,
                 rows_count = showed,
                 offset = offset,
                 limit = limit,
                 colspan = len(names),
                 names = names,
                 rows = rows,
#                sequence = True,
                 debug = str(s),
               )
