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

from .. import app, require_ext


@app.route('/query/')
@login_required
def views_query():
    dbs_list = getDbList(current_user.home)

    flash("Выберите базу данных")
    return render_template('dump_list.html',
             obj_a = dbs_list,
           )


@app.route('/query/<db>/')
@login_required
def views_query_db(db):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    sqltemplates = SQLTemplate.query.all()

    names = ['SQL query', 'Description']
    rows = [['<a href="{0}">{1}</a>'.format(url_for('views_query_db_id', db=db, id=sqltemplate.id),
             sqltemplate.name if sqltemplate.name else "<{0}>".format(sqltemplate.id)),
             '<a href="{0}">{1}</a>'.format(url_for('views_query_db_dump', db=db, id=sqltemplate.id),
             sqltemplate.description if sqltemplate.description else '>')
           ] for sqltemplate in sqltemplates]

    return render_template('dump_table_unsafe.html',
             names = names,
             rows = rows,
           )


@app.route('/query/<db>/dump/<id>/')
@login_required
def views_query_db_dump(db, id):
    dbs_list = getDbList(current_user.home)

    sqltemplate = SQLTemplate.query.filter_by(
      id = id,
    ).first()

    return html(sqltemplate.value)


@app.route('/query/<db>/<id>')
@login_required
def views_query_db_id(db, id):
    db_uri, session, metadata = initDb(current_user.home, db)
    if not db_uri:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    sqltemplate = SQLTemplate.query.filter_by(
      id = id,
    ).first()
    if not sqltemplate:
        flash("Базы данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    res = session.execute(sqltemplate.value)
    names = res.keys()
    rows = [[j for j in i] for i in res.fetchall()]

    return render_template_custom('dump_table.html',
             names = names,
             rows = rows,
           )
