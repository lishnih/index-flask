#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-26

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from collections import OrderedDict

from flask import request, render_template, jsonify, url_for, flash

from flask_login import login_required, current_user

from sqlalchemy.sql import select

from ..core.backwardcompat import *
from ..core.db import getDbList, initDb, get_relative_tables, get_rows_base
from ..core.dump_html import html

from .. import app


@app.route('/db/')
@app.route('/db/<db>/')
@login_required
def views_db(db=None):
    dbs_list = getDbList(current_user.home)

    names = ['Db/View', 'Info', 'Session', 'Metadata']
    dbs_list = [['<a href="{0}">{1}</a>'.format(url_for('views_db', db=dbname), dbname),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=dbname), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_session', db=dbname), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_metadata', db=dbname), '>'),
               ] for dbname in dbs_list]

    group = []
    if db:
        db_uri, session, metadata = initDb(current_user.home, db)
        if not db_uri:
            flash("Базы данных не существует: {0}".format(db), 'error')
            return render_template('p/empty.html')

        else:
            table_names = ['View']
            tables = [['<a href="{0}">{1}</a>'.format(url_for('views_db_table', db=db, table=table), table),
                     ] for table in metadata.tables.keys()]

            group.append((db, table_names, tables))

    return render_template('views/views_user_db/index.html',
             title = 'Databases',
             names = names,
             dbs_list = dbs_list,
             group = group,
           )


@app.route('/db/session/<db>/')
@login_required
def views_db_session(db):
    dbs_list = getDbList(current_user.home)

    names = ['Db/View', 'Info', 'Session', 'Metadata']
    dbs_list = [['<a href="{0}">{1}</a>'.format(url_for('views_db', db=dbname), dbname),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=dbname), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_session', db=dbname), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_metadata', db=dbname), '>'),
               ] for dbname in dbs_list]

    group = []
    if db:
        db_uri, session, metadata = initDb(current_user.home, db)

    return html(session)


@app.route('/db/metadata/<db>/')
@login_required
def views_db_metadata(db):
    dbs_list = getDbList(current_user.home)

    names = ['Db/View', 'Info', 'Session', 'Metadata']
    dbs_list = [['<a href="{0}">{1}</a>'.format(url_for('views_db', db=dbname), dbname),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=dbname), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_session', db=dbname), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_metadata', db=dbname), '>'),
               ] for dbname in dbs_list]

    group = []
    if db:
        db_uri, session, metadata = initDb(current_user.home, db)

    return html(metadata)


@app.route('/db/info/<db>')
@login_required
def views_db_info(db):
    dbs_list = getDbList(current_user.home)

    names = ['Db/View', 'Info', 'Session', 'Metadata']
    dbs_list = [['<a href="{0}">{1}</a>'.format(url_for('views_db', db=dbname), dbname),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=dbname), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_session', db=dbname), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_metadata', db=dbname), '>'),
               ] for dbname in dbs_list]

    group = []
    if db:
        db_uri, session, metadata = initDb(current_user.home, db)
        if not db_uri:
            flash("Базы данных не существует: {0}".format(db), 'error')
            return render_template('p/empty.html')

        else:
            group = [(db, None, [[]])]
            table_names = ['Column', 'type', 'primary_key', 'nullable', 'index', 'autoincrement', 'unique', 'default', 'foreign_keys', 'onupdate']
            for table, mtable in metadata.tables.items():
                tables = []
                for c in mtable.c:
                    tables.append(['<a href="{0}">{1}</a>'.format(url_for('views_db_table_column_distinct', db=db, table=table, column=c.name), c.name),
                                   '<a href="{0}">{1}</a>'.format(url_for('views_db_table_column_info', db=db, table=table, column=c.name), repr(c.type)),
                                   c.primary_key, c.nullable, c.index, c.autoincrement, c.unique, c.default, c.foreign_keys, c.onupdate])

                table = '<a href="{0}">{1}</a>'.format(url_for('views_db_table_info', db=db, table=table), table)
                group.append((table, table_names, tables))

    return render_template('views/views_user_db/index.html',
             title = 'Database Info',
             names = names,
             dbs_list = dbs_list,
             group = group,
           )


@app.route('/db/info/<db>/<table>')
@login_required
def views_db_table_info(db, table):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    return html(metadata.tables.get(table))


@app.route('/db/info/<db>/<table>/<column>')
@login_required
def views_db_table_column_info(db, table, column):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    mtable = metadata.tables.get(table)

    return html(mtable.c.get(column))


@app.route('/db/distinct/<db>/<table>/<column>')
@login_required
def views_db_table_column_distinct(db, table, column):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    mtable = metadata.tables.get(table)

    s = select([mtable.c.get(column).distinct()]).select_from(mtable)
    res = session.execute(s)
    rows = [i[0] for i in res.fetchall()]
    total = len(rows)

    return html([total, rows])


@app.route('/db/<db>/<table>/', methods=["GET", "POST"])
@login_required
def views_db_table(db, table):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    mtable = metadata.tables.get(table)

    offset = int(request.form.get('offset', 0))
    limit = int(request.form.get('limit', 100))

    if 'all' in request.args.keys():
        offset = 0
        limit = 0

    names, rows, total, filtered, showed, page, pages, s = get_rows_base(session, mtable, offset, limit)

    # Необходимые переменные
    colspan = len(names)

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
        return render_template('views/views_user_db/table.html',
                 title = 'Database: {0}'.format(db),
                 db = db,
                 full_rows_count = total,
                 filtered_rows_count = filtered,
                 rows_count = showed,
                 offset = offset,
                 limit = limit,
                 colspan = colspan,
                 names = names,
                 rows = rows,
#                sequence = True,
                 debug = str(s),
               )
