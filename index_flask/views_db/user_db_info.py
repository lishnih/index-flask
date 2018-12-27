#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-26

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json

from flask import request, render_template, jsonify, url_for, flash
from jinja2 import Markup, escape

from flask_login import login_required, current_user

from sqlalchemy import not_, and_
from sqlalchemy.sql import select, text

from ..main import app
from ..core.db import (init_db, get_dbs_list, get_rows_base, get_rows_ext,
                       get_primary_tables)
from ..core.db_session import db_session, db_session_metadata
from ..core.dump_html import html
from ..core.functions import debug_query
from ..core.render_response import render_format
from ..core.user_templates import get_user_templates
from ..views_db.user_db import get_db_list, get_db


# ===== Routes =====

@app.route('/db_info/')
@login_required
def user_db_info():
    databases = get_db_list(current_user)
    obj = []
    without_sidebar = False

    db = request.values.get('db', '')
    if db:
        user_db = get_db(current_user, db)
        if not user_db:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('db/user_db_info.html')

        with db_session_metadata(user_db.uri) as (session, metadata):
            table_names = ['Column', 'type', 'primary_key', 'nullable', 'index', 'autoincrement',
                           'unique', 'default', 'foreign_keys', 'onupdate']
            for table, mtable in metadata.tables.items():
                table_rows = []
                for c in mtable.c:
                    table_rows.append([Markup('<a href="{0}">{1}</a>'.format(url_for('user_db_info_column_distinct',
                                         db=escape(db), table=escape(table), column=escape(c.name)), escape(c.name))),
                                       Markup('<a href="{0}">{1}</a>'.format(url_for('user_db_info_column',
                                         db=escape(db), table=escape(table), column=escape(c.name)), repr(c.type))),
                                       c.primary_key, c.nullable, c.index, c.autoincrement,
                                       c.unique, c.default, c.foreign_keys, c.onupdate])

                table = '<a href="{0}">{1}</a>'.format(url_for('user_db_info_table', db=db, table=table), table)
                obj.append((table_names, table_rows, table, ''))

            without_sidebar = True

    return render_template('db/user_db_info.html',
        title = 'Databases',
        without_sidebar = without_sidebar,
        databases = databases,
        tables_wdest = obj,
    )


@app.route('/db_info/session')
@login_required
def user_db_info_session():
    databases = get_db_list(current_user)
    obj = []

    db = request.values.get('db', '')
    if db:
        user_db = get_db(current_user, db)
        if not user_db:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('db/user_db_info.html')

        with db_session(user_db.uri) as session:
            return render_template('db/user_db_info.html',
                title = 'Session',
                databases = databases,
                html = html(session),
            )


@app.route('/db_info/metadata')
@login_required
def user_db_info_metadata():
    databases = get_db_list(current_user)
    obj = []

    db = request.values.get('db', '')
    if db:
        user_db = get_db(current_user, db)
        if not user_db:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('db/user_db_info.html')

        with db_session_metadata(user_db.uri) as (session, metadata):
            return render_template('db/user_db_info.html',
                title = 'Metadata',
                databases = databases,
                html = html(metadata),
            )


@app.route('/db_info/table')
@login_required
def user_db_info_table():
    databases = get_db_list(current_user)
    obj = []

    db = request.values.get('db', '')
    table = request.values.get('table', '')
    if db and table:
        user_db = get_db(current_user, db)
        if not user_db:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('db/user_db_info.html')

        with db_session_metadata(user_db.uri) as (session, metadata):
            mtable = metadata.tables.get(table)
            if mtable is None:
                flash("Таблицы не существует: {0}".format(table), 'error')
                return render_template('db/user_db_info.html')

            return render_template('db/user_db_info.html',
                title = 'Metadata',
                databases = databases,
                html = html(mtable),
            )


@app.route('/db_info/column')
@login_required
def user_db_info_column():
    databases = get_db_list(current_user)
    obj = []

    db = request.values.get('db', '')
    table = request.values.get('table', '')
    column = request.values.get('column', '')
    if db and table and column:
        user_db = get_db(current_user, db)
        if not user_db:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('db/user_db_info.html')

        with db_session_metadata(user_db.uri) as (session, metadata):
            mtable = metadata.tables.get(table)
            if mtable is None:
                flash("Таблицы не существует: {0}".format(table), 'error')
                return render_template('db/user_db_info.html')

            mcolumn = mtable.c.get(column)
            if mcolumn is None:
                flash("Колонки не существует: {0}".format(column), 'error')
                return render_template('db/user_db_info.html')

            return render_template('db/user_db_info.html',
                title = 'Metadata',
                databases = databases,
                html = html(mcolumn),
            )


@app.route('/db_info/distinct')
@login_required
def user_db_info_column_distinct():
    databases = get_db_list(current_user)
    obj = []

    db = request.values.get('db', '')
    table = request.values.get('table', '')
    column = request.values.get('column', '')
    if db and table and column:
        user_db = get_db(current_user, db)
        if not user_db:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('db/user_db_info.html')

        with db_session_metadata(user_db.uri) as (session, metadata):
            mtable = metadata.tables.get(table)
            if mtable is None:
                flash("Таблицы не существует: {0}".format(table), 'error')
                return render_template('db/user_db_info.html')

            mcolumn = mtable.c.get(column)
            if mcolumn is None:
                flash("Колонки не существует: {0}".format(column), 'error')
                return render_template('db/user_db_info.html')

            names = ['Values']
            s = select([mcolumn.distinct()], mtable).order_by(mcolumn)
            res = session.execute(s)
            rows = [[i[0]] for i in res.fetchall()]

            return render_template('base.html',
                     names = names,
                     rows = rows,
                     total = len(rows),
                   )
