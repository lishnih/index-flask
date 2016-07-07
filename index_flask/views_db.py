#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-26

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from collections import OrderedDict

from flask import request, jsonify, render_template

from flask_login import login_required, current_user

from .core.backwardcompat import *
from .core.dump_html import html
from .view_j2.query_interface import qi_query
from .extensions import user_db

from . import app


@app.route('/db/')
@app.route('/db/<db>/')
@login_required
def view_db(db=None):
    dbs_list = user_db.get_dbs_list(current_user)

    if db:
        db_uri, session, metadata = user_db.get_db(current_user, db)
        tables = metadata.tables.keys()
    else:
        tables = None

    return render_template('db/index.html',
             title = 'Databases',
             dbs_list = dbs_list,
             db = db,
             tables = tables,
           )


@app.route('/db/<db>/<table1>/', methods=["GET", "POST"])
@app.route('/db/<db>/<table1>/<table2>/', methods=["GET", "POST"])
@app.route('/db/<db>/<table1>/<table2>/<table3>/', methods=["GET", "POST"])
@app.route('/db/<db>/<table1>/<table2>/<table3>/<table4>/', methods=["GET", "POST"])
@app.route('/db/<db>/<table1>/<table2>/<table3>/<table4>/<table5>/', methods=["GET", "POST"])
@login_required
def view_db_table(db, table1=None, table2=None, table3=None, table4=None, table5=None):
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
        return render_template('db/table.html',
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
                 primarytables = table_info.get('primarytables', []),
                 followedtables = table_info.get('followedtables', []),
                 lasttable = lasttable,
                 error = error,
#                debug = unicode(s),
               )


@app.route('/jtable')
@login_required
def view_db_jtable():
    return render_template('db/jtable.html',
             title = 'View table',
#            debug = unicode(s),
           )


@app.route('/j3', methods=["GET", "POST"])
@login_required
def view_db_j3():
    if request.method == 'POST':
        action = request.args.get('action')
        db = request.args.get('db')
        tables = request.args.get('t').split('|')
        table1 = tables[0]

        if db not in user_db.get_dbs_list(current_user):
            return jsonify(Result="ERROR", Message="Db don't exists!")

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
            plain = 0,
        )

        table_info, rows, error = qi_query(**query_params)


        # Колонки
        names = table_info.get('columns', ['no columns'])
        fields = OrderedDict()
        for name in names:
            fields[name] = {
                'key':    False,
                'create': True,
                'edit':   True,
                'list':   True,
                'title':  name,
            }


        if action == 'list':

            res = {
              "Result": "OK",
              "Records": rows,
            }

        elif action == 'create':
            res = {
              "Result": "ERROR",
              "Message": "Access denied!",
            }

        elif action == 'update':
            res = {
              "Result": "ERROR",
              "Message": "Access denied!",
            }

        elif action == 'delete':
            res = {
              "Result": "ERROR",
              "Message": "Access denied!",
            }

        elif action == 'columns':
            res = OrderedDict(
              Result = "OK",
              fields = fields,
#             "debug": html(request),
            )

        elif action == 'primarytables':
            res = {
              "Result": "OK",
              "primarytables": table_info.get('primarytables', []),
#             "debug": html(s_count),
            }

        else:
            res = {
              "Result": "ERROR",
              "Message": "Action unknown!",
            }

        return jsonify(**res)
    return "no output"
