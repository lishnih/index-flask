#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-21

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, render_template, redirect, url_for, jsonify, flash

from flask_login import login_required, current_user

from ..app import app, db
from ..core.functions import get_next
from ..forms.database import AddDatabaseForm
from ..models.database import Database
from ..models.group import Group


# ===== Interface =====

def json_required(form):
    return 'type' in form and form.type.data == 'json'


def get_db_list(user):
    db_list = db.session.query(Database).filter_by(user=user).all()
    for i in db_list:
        yield i.name


def get_db(user, dbname):
    return db.session.query(Database).filter_by(user=user, name=dbname).first()


def set_default_db(user, dbname):
    user_db = get_db(user, dbname)
    if not user_db:
        return None

    user_db.default = True
    db.session.commit()

    return user_db


def default_db(user):
    return db.session.query(Database).filter_by(user=user, default=True).first()


# ===== Routes =====

@app.route('/db/')
@login_required
def user_db():
    return render_template('db/user_db_info.html',
        databases = [i.name for i in current_user.databases],
    )


@app.route('/db/set_default')
@login_required
def user_db_set_default():
    dbname = request.values.get('db')
    if not dbname:
        flash('Database required!')
        return render_template('base.html')

    user_db = set_default_db(current_user, dbname)
    if not user_db:
        flash('Database not found!')
        return render_template('base.html')

    return render_template('base.html',
        text = "The database '{0}' installed by default!".format(user_db.name),
    )


@app.route('/db/default')
@login_required
def user_db_default():
    user_db = default_db(current_user)
    if not user_db:
        flash('Database not found!')
        return render_template('base.html')

    return render_template('base.html',
        text = "The default database: '{0}'!".format(user_db.name),
    )


@app.route('/db/append', methods=['GET', 'POST'])
@login_required
def user_db_append():
    form = AddDatabaseForm(request.form)

    if request.method == 'POST':
        if form.validate():
            user_db = Database(
                name = form.name.data,
                uri = form.uri.data,
                user = current_user,
            )
            db.session.add(user_db)
            db.session.commit()

            if json_required(form):
                return jsonify({'result': 'ok'})

            flash('Successfully append {0}'.format(form.name.data))
            return render_template('db/append_db.html',
                form = form,
            )

        else:
            if json_required(form):
                return jsonify({'result': 'error', 'message': 'Invalid data!'})

    return render_template('db/append_db.html',
        form = form,
    )


@app.route('/db/new', methods=['GET', 'POST'])
@login_required
def user_db_new():
    form = AddDatabaseForm(request.form)

    if request.method == 'POST':
        if form.validate():
            user_db = Database(
                name = form.name.data,
                uri = form.uri.data,
                user = current_user,
            )
            db.session.add(user_db)
            db.session.commit()

            if json_required(form):
                return jsonify({'result': 'ok'})

            flash('Successfully create {0}'.format(form.name.data))
            return render_template('db/append_db.html',
                form = form,
            )

        else:
            if json_required(form):
                return jsonify({'result': 'error', 'message': 'Invalid data!'})

    return render_template('db/append_db.html',
        form = form,
    )


@app.route('/db/delete')
@login_required
def user_db_delete():
    dbname = request.values.get('db', '')
    user_db = get_db(current_user, dbname)
    db.session.delete(user_db)
    db.session.commit()

    return redirect(get_next(back=True))
