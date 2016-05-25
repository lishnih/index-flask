#!/usr/bin/env python
# coding=utf-8
# Stan 2013-05-15, 2016-04-24

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import logging
from flask import Flask, g, url_for, render_template, send_from_directory
from sqlalchemy.sql import select

from .lib.backwardcompat import *
from .lib.db import initDb
from .lib.dump_html import html
from .lib.fileman import list_files
from .lib.settings import Settings


app = Flask(__name__, static_url_path='')


def get_conn():
    if 'engine' not in g:
        s = Settings()
        g.db_uri = "{0}:///{1}/{2}".format('sqlite', s.system.path, 'xls0p3.sqlite')
        g.engine, g.metadata, g.tables, g.relationships = initDb(g.db_uri)
    return g.engine.connect()


@app.route("/")
def hello():
    return app.send_static_file('index.html')


@app.route('/test/')
@app.route('/test/<path:path>')
def view_test(path=''):
    if not path or path[-1] == '/':
        test_url = '/test/{0}'.format(path)
        dirlist, filelist = list_files(test_url, app.root_path)
        return render_template('direntries.html', path=test_url, dirlist=dirlist, filelist=filelist)
    else:
        return send_from_directory('test', path)


@app.route('/user/<username>')
def profile(username):
    return 'User {0}'.format(username)


@app.route('/login')
def login():
    pass


@app.route('/app')
def view_app():
    return html(app)


@app.route('/g')
def view_g():
    get_conn()
    return html(g)


@app.route('/dbinfo')
def view_dbinfo():
    get_conn()
    return html(g.tables)


@app.route('/dbinfo/<table>')
def view_tableinfo(table=None):
    get_conn()
    if table in g.tables:
        return html(g.metadata.tables.get(table))
    else:
        return 'No such table!'


@app.route('/rel')
def view_rel():
    get_conn()
    return html(g.relationships)


@app.route('/debug')
def view_debug():
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        output.append([rule.endpoint, methods, url])

    return render_template('listurls.html', urls=sorted(output))


@app.route('/db/')
def view_db():
    get_conn()
    return render_template('listdbs.html', dbs=g.tables)


@app.route('/db/<table1>/')
@app.route('/db/<table1>/<table2>/')
@app.route('/db/<table1>/<table2>/<table3>/')
@app.route('/db/<table1>/<table2>/<table3>/<table4>/')
@app.route('/db/<table1>/<table2>/<table3>/<table4>/<table5>/')
def view_table(table1=None, table2=None, table3=None, table4=None, table5=None):
    conn = get_conn()

    # Обратный порядок - не менять!
    tables = [i for i in [table5, table4, table3, table2, table1] if i]

    mtables = [g.metadata.tables.get(i) for i in tables]
    s = select(mtables, offset=0, limit=100, use_labels=True)
    s_count = select(mtables, use_labels=True)

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

#   return unicode(s)
#   mtable.join(mtable2, mtable.c._files_id==mtable2.c.id)

    result = conn.execute(s.select_from(mtable))
    rows = [row for row in result]

    count = conn.execute(s_count.select_from(mtable).count())
    count = count.first()[0]


    names = [[column.table.name, column.name] for name, column in s._columns_plus_names]
    extratables = [i.column.table.name for i in s.foreign_keys]
    lasttable = tables[0] if len(tables) > 1 else None
    return render_template('listrows.html', count=count, rows=rows, names=names, tables=tables,
                           extratables=extratables, lasttable=lasttable, error=error, debug=s)



if __name__ == "__main__":
    app.run(debug=True)
