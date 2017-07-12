#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-11

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import request, render_template, jsonify, url_for, flash

from flask_login import login_required, current_user

from sqlalchemy.sql import select

from ..core.backwardcompat import *
from ..core.db import getDbList, initDb
from ..core.render_template_custom import render_template_custom
from ..core.dump_html import html
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
            flash("Базы данных не существует: {0}".format(db), 'error')
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

    return html(sqltemplate.value)


@app.route('/query/<db>/<id>')
@login_required
def views_query_db_id(db, id):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    sqltemplate = SQLTemplate.query.filter_by(id=id).first()
    if not sqltemplate:
        flash("Запроса не существует: {0}".format(id), 'error')
        return render_template('p/empty.html')

    res = session.execute(sqltemplate.value)
    names = res.keys()
    rows = [[j for j in i] for i in res.fetchall()]

    return render_template_custom('dump_table.html',
             names = names,
             rows = rows,
           )
