#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json

from flask import request, redirect, flash

from flask_login import login_required, current_user

from sqlalchemy.sql import select, func, text, column, table, and_

from ..app import app, db
from ..core.functions import get_next
from ..core.render_response import render_ext
from ..forms.user_task import AddUserTaskForm
from ..models.handler import Handler
from ..models.source import Source
from ..models.user_task import UserTask


# ===== Interface =====

def user_task_create(user_source, handler, mode='manual'):
    if handler == 'scan_files':
        handler = Handler.query.filter_by(name='scan_files', user=None).first()

    user_task = UserTask(
        user = current_user,
        source = user_source,
        handler = handler,
        mode = mode,
    )

    db.session.add(user_task)
    db.session.commit()

#   if mode == 'auto':
#       user_task_request(user_task)

    return user_task


# ===== Routes =====

@app.route('/source/schedule')
@login_required
def user_tasks():
    user_tasks = db.session.query(UserTask).filter_user(True).join(Source, isouter=True).filter_user(True).all()

    return render_ext('db/user_tasks.html',
        user_tasks = user_tasks,
    )


@app.route('/user_task/configure', methods=['GET', 'POST'])
@login_required
def user_task_configure():
    uid = request.values.get('uid')
    name = request.values.get('name')

    user_task = db.session.query(UserTask).filter_active().filter_by(uid=uid).first()
    if not user_task:
        return render_ext('base.html',
            message = ("User task not found: {0}".format(name), 'danger')
        )

    return render_ext('db/user_task.html',
        user_task = user_task,
    )


@app.route('/user_task/append', methods=['GET', 'POST'])
@login_required
def user_task_append():
    sources = Source.query.filter_user(True).all()
    handlers = Handler.query.filter_user(True).all()
    form = AddUserTaskForm(request.form, sources, handlers)

    message = ''
    if request.method == 'POST':
        if form.validate():
            user_task_create(form.user_source, form.user_handler, form.handling.data)
            message = "The task successfully added!"

        else:
            message = 'Invalid data!', 'danger'

    return render_ext('db/append_user_task.html',
        message = message,
        form = form,
    )


@app.route('/user_task/delete', methods=['GET', 'POST'])
@login_required
def user_task_delete():
    uid = request.values.get('uid')
    name = request.values.get('name')

    user_task = db.session.query(UserTask).filter_active().filter_by(uid=uid).first()
    if not user_task:
        return render_ext('base.html',
            message = ("User task not found: {0}".format(name), 'danger')
        )

    user_task.deleted = True
    db.session.commit()

    return redirect(get_next(back=True))
