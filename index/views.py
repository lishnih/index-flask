#!/usr/bin/env python
# coding=utf-8
# Stan 2013-05-15, 2016-04-24

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import ( g, request, jsonify, render_template,
                    redirect, url_for, abort )

from flask_login import login_required, current_user

from sqlalchemy.sql import select

from .ext.backwardcompat import *
from .ext.dump_html import html

from . import app, get_conn


@app.route("/")
def index():
#   return app.send_static_file('index.html')

    username = None if current_user.is_anonymous else current_user.username
    return render_template('index.html', username=username)


@app.route('/db/')
@login_required
def view_db():
    get_conn()
    return render_template('view_db.html', 
             title = 'Databases',
             dbs = g.metadata.tables.keys(),
#            debug = html(g),
           )


@app.route('/db/<table1>/', methods=["GET", "POST"])
@app.route('/db/<table1>/<table2>/', methods=["GET", "POST"])
@app.route('/db/<table1>/<table2>/<table3>/', methods=["GET", "POST"])
@app.route('/db/<table1>/<table2>/<table3>/<table4>/', methods=["GET", "POST"])
@app.route('/db/<table1>/<table2>/<table3>/<table4>/<table5>/', methods=["GET", "POST"])
@login_required
def view_table(table1=None, table2=None, table3=None, table4=None, table5=None):
    conn = get_conn()

    # Обратный порядок - не менять!
    tables = [i for i in [table5, table4, table3, table2, table1] if i]

    # Список таблиц
    mtables = [g.metadata.tables.get(i) for i in tables]

    # Список колонок
    mcolumns = []
    for i in mtables:
        if i is None:
            abort(404)    # Table not exist
        mcolumns.extend(j for j in i.c if not j.foreign_keys and not j.primary_key and j.name[0] != '_')
    colspan = len(mcolumns)

    # Join для таблиц
    error = None
    mtable = g.metadata.tables.get(table1)

    l = len(tables) - 1
    for i in range(l):
        for j in mtables[l - i].foreign_keys:
            if j.column.table == mtables[l - i - 1]:
                mtable = mtable.join(mtables[l - i - 1], j.parent==j.column)
                break
        else:
            error = 'Error!'

    # Получаем кол-во всех записей в таблице
    s_count = select(mtables, use_labels=True)
    count = conn.execute(s_count.select_from(mtable).count())
    count = count.first()[0]

    # Получаем записи
    if 'all' in request.args.keys():
        offset = 0
        limit = count
        s = select(mcolumns, use_labels=True)
    else:
        offset = int(request.form.get('offset')) if request.method == 'POST' else 0
        limit = 100
        s = select(mcolumns, offset=offset, limit=limit, use_labels=True)

    result = conn.execute(s.select_from(mtable))
    rows = [row for row in result]

    # Необходимые переменные
    names = [[column.table.name, column.name] for name, column in s._columns_plus_names]
    extratables = [i.column.table.name for i in s_count.foreign_keys]   # s_count!
    extratables = [i for i in extratables if i not in tables]
    lasttable = tables[0] if len(tables) > 1 else None

    # Выводим
    if request.method == 'POST':
        return jsonify(
                 count = count,
                 offset = offset,
                 limit = limit,
                 rows=[[j for j in i] for i in rows],
               )
    else:
        return render_template('view_table.html',
                 title = 'Database: {0}'.format(table1),
                 count = count,
                 offset = offset,
                 limit = limit,
                 colspan = colspan,
                 rows = rows,
                 names = names,
                 tables = tables,
                 extratables = extratables,
                 lasttable = lasttable,
                 error = error,
#                debug = unicode(s),
               )


@app.route('/jtable')
@login_required
def view_jtable():
    return render_template('view_jtable.html',
#            debug = unicode(s),
           )


@app.route('/j3', methods=["GET", "POST"])
@login_required
def view_j3():
    conn = get_conn()

    if request.method == 'POST':
        action = request.args.get('action')
        tables = request.args.get('t').split(',')
        table1 = tables[0]

        # Список таблиц
        mtables = [g.metadata.tables.get(i) for i in tables]

        # Список колонок
        mcolumns = []
        for i in mtables:
            if i is None:
                return jsonify(Result="ERROR", Message="Table is missing!")

            mcolumns.extend(j for j in i.c)

        # Join для таблиц
        error = None
        mtable = g.metadata.tables.get(table1)

        l = len(tables) - 1
        for i in range(l):
            for j in mtables[i].foreign_keys:
                if j.column.table == mtables[i + 1]:
                    mtable = mtable.join(mtables[i + 1], j.parent==j.column)
                    break
            else:
                error = 'Error!'

        # Получаем кол-во всех записей в таблице
        s_count = select(mtables, use_labels=True)
        count = conn.execute(s_count.select_from(mtable).count())
        count = count.first()[0]

        # Колонки
        names = []
        fields = {}
        for name, column in s_count._columns_plus_names:  # s_count!
            columnname = "{0}.{1}".format(column.table.name, column.name)
            names.append(name)
            key = True if column.foreign_keys or column.primary_key or column.name[0] == '_' else False
            fields[name] = {
                'key':    True  if key else False,
                'create': False if key else True,
                'edit':   False if key else True,
                'list':   False if key else True,
                'title':  columnname,
            }

        if action == 'list':
            # Получаем записи
            offset = 0
            limit = 100
            s = select(mcolumns, offset=offset, limit=limit, use_labels=True)

            result = conn.execute(s.select_from(mtable))

            rows = []
            for row in result:
                rows.append(dict(zip(names, row)))

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
            res = {
              "Result": "OK",
              "fields": fields,
#             "debug": html(request),
            }

        elif action == 'extratables':
            extratables = [i.column.table.name for i in s_count.foreign_keys]   # s_count!
            extratables = [i for i in extratables if i not in tables]

            res = {
              "Result": "OK",
              "extratables": extratables,
#             "debug": html(s_count),
            }

        else:
            res = {
              "Result": "ERROR",
              "Message": "Action unknown!",
            }

        return jsonify(**res)
    return "no output"
