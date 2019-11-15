#!/usr/bin/env python
# coding=utf-8
# Stan 2019-01-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json

from flask import request

from flask_login import login_required
from flask_principal import Permission, RoleNeed

from ..app import app, db
from ..core.render_response import render_ext
from ..forms.user_task import AddUserTaskForm
from ..models.handler import Handler
from ..models.source import Source
from ..models.user_task import UserTask


# ===== Roles =====

admin_permission = Permission(RoleNeed('admin'))


# ===== Routes =====

@app.route('/admin/handlers')
@login_required
@admin_permission.require(403)
def admin_handlers():
    return render_ext('db/user_handlers.html',
        handlers = Handler.query.all(),
    )


@app.route('/admin/sources')
@login_required
@admin_permission.require(403)
def admin_sources():
    return render_ext('db/user_sources.html',
        sources = Source.query.all(),
    )


@app.route('/admin/source/schedule')
@login_required
@admin_permission.require(403)
def admin_tasks():
    return render_ext('db/user_tasks.html',
        user_tasks = db.session.query(UserTask).join(Source, isouter=True).all(),
    )


@app.route('/admin/tasks/configure', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def admin_task_configure():
    uid = request.values.get('uid')
    name = request.values.get('name')

    user_task = db.session.query(UserTask).filter_by(uid=uid).first()
    if not user_task:
        return render_ext('base.html',
            message = ("User task not found: {0}".format(name), 'danger')
        )

    return render_ext('db/user_task.html',
        user_tasks = user_task,
    )


@app.route('/admin/task/append', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def admin_task_append():
    handlers = Handler.query.all()
    sources = Source.query.all()
    form = AddUserTaskForm(request.form, sources, handlers)

    message = ''
    if request.method == 'POST':
        if form.validate():
            user_tasks_create(form.user_source, form.user_handler, form.handling.data)
            message = "The task successfully added!"

        else:
            message = 'Invalid data!', 'danger'

    return render_ext('db/append_user_tasks.html',
        message = message,
        form = form,
    )
