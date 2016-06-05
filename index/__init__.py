#!/usr/bin/env python
# coding=utf-8
# Stan 2013-05-15, 2016-04-24

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, logging
from flask import ( Flask, g, request, jsonify, url_for, render_template,
                    send_from_directory, abort, __version__ )
from sqlalchemy.sql import select

from .ext.backwardcompat import *
from .ext.db import initDb
from .ext.dump_html import html
from .ext.fileman import list_files
from .ext.settings import Settings


app = Flask(__name__, static_url_path='')


def get_conn():
    if 'engine' not in g:
        s = Settings()
        g.db_uri = "{0}:///{1}/{2}".format('sqlite', s.system.path, 'xls0p3.sqlite')
        g.engine, g.metadata, g.relationships = initDb(g.db_uri)
    return g.engine.connect()


@app.route("/")
def hello():
    return app.send_static_file('index.html')


# @app.route('/user/<username>')
# def profile(username):
#     return 'User {0}'.format(username)


@app.route('/login')
def login():
    return ''


@app.route('/debug')
def view_debug():
    if not app.debug:
        abort(404)

    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        output.append([rule.endpoint, methods, url])

    return render_template('view_debug.html',
             title = 'Url mapping',
             urls = sorted(output),
           )


@app.route('/test/')
@app.route('/test/<path:path>')
def view_test(path=''):
    if not app.debug:
        abort(404)

    if not path or path[-1] == '/':
        test_url = '/test/{0}'.format(path)
        dirlist, filelist = list_files(test_url, app.root_path)
        return render_template('view_test.html',
                 title = 'Testing directory',
                 path = test_url,
                 dirlist = dirlist,
                 filelist = filelist,
               )
    else:
        return send_from_directory(os.path.join(app.root_path, 'test'), path)
#       return send_from_directory('test', path)


@app.route('/user/')
def view_user():
    if not app.debug:
        abort(404)

    user_url = '/{0}/user/'.format(app.template_folder)
    dirlist, filelist = list_files(user_url, app.root_path, '/user/')
    return render_template('view_test.html',
             title = 'User templates directory',
             path = '/user/',
             dirlist = dirlist,
             filelist = filelist,
           )


@app.route('/user/<path:path>')
def view_user_path(path=''):
    if not app.debug:
        abort(404)

    user_html = 'user/{0}'.format(path)
    return render_template(user_html,
             title = 'User',
           )


@app.route('/ver')
def view_ver():
    if not app.debug:
        abort(404)

    return __version__


@app.route('/app')
def view_app():
    if not app.debug:
        abort(404)

    return html(app)


@app.route('/g')
def view_g():
    if not app.debug:
        abort(404)

    get_conn()
    return html(g)


@app.route('/rel')
def view_rel():
    if not app.debug:
        abort(404)

    get_conn()
    return html(g.relationships)


@app.route('/dbinfo/')
def view_dbinfo():
    if not app.debug:
        abort(404)

    get_conn()
#   return g.db_uri + '<br />' + html(g.metadata)
#   return render_template('dump_dict.html', obj=g.tables)
    return render_template('view_dbinfo.html',
             title = 'Databases info',
             uri = g.db_uri,
             dbs = g.metadata.tables.keys(),
             debug = html(g.metadata),
           )


@app.route('/dbinfo/<table>')
def view_tableinfo(table=None):
    if not app.debug:
        abort(404)

    get_conn()
    if table in g.metadata.tables.keys():
        return html(g.metadata.tables.get(table))
    else:
        return 'No such table!'


@app.route('/db/')
def view_db():
    get_conn()
    return render_template('view_db.html', 
             title = 'Databases',
             dbs = g.metadata.tables.keys(),
           )


@app.route('/db/<table1>/', methods=["GET", "POST"])
@app.route('/db/<table1>/<table2>/', methods=["GET", "POST"])
@app.route('/db/<table1>/<table2>/<table3>/', methods=["GET", "POST"])
@app.route('/db/<table1>/<table2>/<table3>/<table4>/', methods=["GET", "POST"])
@app.route('/db/<table1>/<table2>/<table3>/<table4>/<table5>/', methods=["GET", "POST"])
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
def view_jtable():
    return render_template('view_jtable.html',
#            debug = unicode(s),
           )


@app.route('/j3', methods=["GET", "POST"])
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


if __name__ == "__main__":
    app.run(debug=True)
