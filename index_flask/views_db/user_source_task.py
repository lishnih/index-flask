#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, redirect

from flask_login import login_required, current_user

from sqlalchemy.sql import select, func, text, column, table, and_

from ..main import app, db
from ..core.functions import get_next
from ..core.render_response import render_ext
from ..core.source_task import source_task_create, source_task_request
from ..forms.source_task import AddSourceTaskForm
from ..models.handler import Handler
from ..models.source import Source
from ..models.source_task import SourceTask


# ===== Interface =====

def get_source_task(uid):
    return db.session.query(SourceTask).filter_by(uid=uid).first()


# ===== Routes =====

@app.route('/source/schedule')
@login_required
def user_source_tasks():
    source_tasks = db.session.query(SourceTask).filter_active().join(Source).filter_user().all()

    return render_ext('db/user_source_tasks.html',
        source_tasks = source_tasks,
    )


@app.route('/source_task/run')
@login_required
def user_source_task_run():
    uid = request.values.get('uid')
    name = request.values.get('name')
    result_m = 'ok'

    user_source_task = db.session.query(SourceTask).filter_active().filter_by(uid=uid).first()
    if not user_source_task:
        result_m = 'error', "User task not found: {0}".format(name)
        return render_ext('base.html', result_m)

    source_task_request(user_source_task)

    return redirect(get_next(back=True))


@app.route('/source_task/configure', methods=['GET', 'POST'])
@login_required
def user_source_task_configure():
    uid = request.values.get('uid')
    name = request.values.get('name')
    result_m = 'ok'

    user_source_task = db.session.query(SourceTask).filter_active().filter_by(uid=uid).first()
    if not user_source_task:
        result_m = 'error', "User task not found: {0}".format(name)
        return render_ext('base.html', result_m)

    return render_ext('db/user_source_task.html', result_m,
        source_task = user_source_task,
    )


@app.route('/source_task/append', methods=['GET', 'POST'])
@login_required
def user_source_task_append():
    result_m = 'ok'
    sources = Source.query.filter(Source.user == current_user).all()
    handlers = Handler.query.filter(Source.user == current_user).all()
    form = AddSourceTaskForm(request.form, sources, handlers)

    if request.method == 'POST':
        if form.validate():
            source_task_create(form.user_source, form.user_handler, form.handling.data)

            result_m = 'ok', "The task successfully added!"

        else:
            result_m = 'error', 'Invalid data!'

    return render_ext('db/append_source_task.html', result_m,
        form = form,
    )


@app.route('/source_task/delete', methods=['GET', 'POST'])
@login_required
def user_source_task_delete():
    uid = request.values.get('uid')
    name = request.values.get('name')
    result_m = 'ok'

    user_source_task = db.session.query(SourceTask).filter_active().filter_by(uid=uid).first()
    if not user_source_task:
        result_m = 'error', "User task not found: {0}".format(name)
        return render_ext('base.html', result_m)

    user_source_task.deleted = True
    db.session.commit()

    return redirect(get_next(back=True))
