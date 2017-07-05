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
from ..core.dump_html import html
from ..view_j2.query_interface import qi_query

from .. import app, require_ext


@app.route('/db/')
@app.route('/db/<db>/')
@login_required
def views_db(db=None):
    user_db = require_ext('user_db', 'html')

    dbs_list = user_db.get_dbs_list(current_user)

    names = ['Db/View', 'Info', 'Session', 'Metadata']
    dbs_list = [['<a href="{0}">{1}</a>'.format(url_for('views_db', db=key), key),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=key), val),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_session', db=key), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_metadata', db=key), '>'),
               ] for key, val in dbs_list.items()]

    group = []
    if db:
        db_uri, session, metadata = user_db.get_db(current_user, db)
        if not db_uri:
            group = [(db, None, [["БД не существует: {0}".format(db)]])]

        else:
            table_names = ['View']
            tables = [['<a href="{0}">{1}</a>'.format(url_for('views_db_table', db=db, table1=table), table),
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
    user_db = require_ext('user_db', 'html')

    dbs_list = user_db.get_dbs_list(current_user)

    names = ['Db/View', 'Info', 'Session', 'Metadata']
    dbs_list = [['<a href="{0}">{1}</a>'.format(url_for('views_db', db=key), key),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=key), val),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_session', db=key), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_metadata', db=key), '>'),
               ] for key, val in dbs_list.items()]

    group = []
    if db:
        db_uri, session, metadata = user_db.get_db(current_user, db)

    return html(session)


@app.route('/db/metadata/<db>/')
@login_required
def views_db_metadata(db):
    user_db = require_ext('user_db', 'html')

    dbs_list = user_db.get_dbs_list(current_user)

    names = ['Db/View', 'Info', 'Session', 'Metadata']
    dbs_list = [['<a href="{0}">{1}</a>'.format(url_for('views_db', db=key), key),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=key), val),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_session', db=key), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_metadata', db=key), '>'),
               ] for key, val in dbs_list.items()]

    group = []
    if db:
        db_uri, session, metadata = user_db.get_db(current_user, db)

    return html(metadata)


@app.route('/db/info/<db>')
@login_required
def views_db_info(db):
    user_db = require_ext('user_db', 'html')

    dbs_list = user_db.get_dbs_list(current_user)

    names = ['Db/View', 'Info', 'Session', 'Metadata']
    dbs_list = [['<a href="{0}">{1}</a>'.format(url_for('views_db', db=key), key),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=key), val),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_session', db=key), '>'),
                 '<a href="{0}">{1}</a>'.format(url_for('views_db_metadata', db=key), '>'),
               ] for key, val in dbs_list.items()]

    group = []
    if db:
        db_uri, session, metadata = user_db.get_db(current_user, db)
        if not db_uri:
            group = [(db, None, [["БД не существует: {0}".format(db)]])]

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
    user_db = require_ext('user_db', 'html')

    dbs_list = user_db.get_dbs_list(current_user)

    db_uri, session, metadata = user_db.get_db(current_user, db)
    if not db_uri:
        return "БД не существует: {0}".format(db)

    return html(metadata.tables.get(table))


@app.route('/db/info/<db>/<table>/<column>')
@login_required
def views_db_table_column_info(db, table, column):
    user_db = require_ext('user_db', 'html')

    dbs_list = user_db.get_dbs_list(current_user)

    db_uri, session, metadata = user_db.get_db(current_user, db)
    if not db_uri:
        return "БД не существует: {0}".format(db)

    mtable = metadata.tables.get(table)

    return html(mtable.c.get(column))


@app.route('/db/distinct/<db>/<table>/<column>')
@login_required
def views_db_table_column_distinct(db, table, column):
    user_db = require_ext('user_db', 'html')

    dbs_list = user_db.get_dbs_list(current_user)

    db_uri, session, metadata = user_db.get_db(current_user, db)
    if not db_uri:
        return "БД не существует: {0}".format(db)

    mtable = metadata.tables.get(table)

    s = select([mtable.c.get(column).distinct()]).select_from(mtable)
    res = session.execute(s)
    rows = [i[0] for i in res.fetchall()]
    total = len(rows)

    return html([total, rows])


@app.route('/db/<db>/<table1>/', methods=["GET", "POST"])
@app.route('/db/<db>/<table1>/<table2>/', methods=["GET", "POST"])
@app.route('/db/<db>/<table1>/<table2>/<table3>/', methods=["GET", "POST"])
@app.route('/db/<db>/<table1>/<table2>/<table3>/<table4>/', methods=["GET", "POST"])
@app.route('/db/<db>/<table1>/<table2>/<table3>/<table4>/<table5>/', methods=["GET", "POST"])
@login_required
def views_db_table(db, table1=None, table2=None, table3=None, table4=None, table5=None):
    # Обратный порядок - не менять!
    tables = [i for i in [table5, table4, table3, table2, table1] if i]

    offset = int(request.form.get('offset', 0))
    limit = int(request.form.get('limit', 100))

    if 'all' in request.args.keys():
        offset = 0
        limit = 0

    query_params = dict(
        user = current_user,
        db = db,
        tables  = tables,
        search  = '',
        filter  = {},
        sorting = [],
        offset  = offset,
        limit   = limit,
        columns = [],
        distinct_columns = [],
        plain = 1,
    )

    table_info, rows, error = qi_query(**query_params)

    # Необходимые переменные
    names = table_info.get('columns', ['no columns'])
    colspan = len(names)

    lasttable = tables[0] if len(tables) > 1 else None

    # Выводим
    if request.method == 'POST':
        return jsonify(
                 full_rows_count = table_info.get('full_rows_count', 0),
                 filtered_rows_count = table_info.get('filtered_rows_count', 0),
                 rows_count = table_info.get('rows_count', 0),
                 offset = offset,
                 limit = limit,
                 rows = rows,
               )
    else:
        if error:
            flash(error, 'error')
        return render_template('views/views_user_db/table.html',
                 title = 'Database: {0}'.format(db),
                 db = db,
                 full_rows_count = table_info.get('full_rows_count', 0),
                 filtered_rows_count = table_info.get('filtered_rows_count', 0),
                 rows_count = table_info.get('rows_count', 0),
                 offset = offset,
                 limit = limit,
                 colspan = colspan,
                 names = names,
                 rows = rows,
                 tables = tables,
                 primary_tables = table_info.get('primary_tables', []),
                 relative_tables = table_info.get('relative_tables', []),
                 lasttable = lasttable,
                 debug = table_info.get('query'),
               )
