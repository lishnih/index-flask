#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json

from flask import request, redirect

from flask_login import login_required

from sqlalchemy.sql import select, func, text, column, table, and_

from ..main import app, db
from ..core.functions import get_next
from ..core.render_response import render_ext
from ..extensions.celery_default_task import run_task_async
from ..forms.source_task import AddSourceTaskForm
from ..models.handler import Handler
from ..models.source import Source
from ..models.source_task import SourceTask


# ===== Interface =====

def get_cloud(user, provider_name):
    usersocialauth = table('social_auth_usersocialauth')
    user_id = column('user_id')
    provider = column('provider')
    s = select(['*'], and_(user_id == user.id, provider == provider_name), usersocialauth)

    res = db.session.execute(s)

    return res.fetchone()


def get_source_task(uid):
    return db.session.query(SourceTask).filter_by(uid=uid).first()


def source_task_create(user_source, handler, mode='manual'):
    if handler == 'scan_files':
        handler = Handler.query.filter_by(name='scan_files').first()
#       mode = 'auto'

    user_source_task = SourceTask(
        source = user_source,
        handler = handler,
        mode = mode,
    )

    db.session.add(user_source_task)
    db.session.commit()

    if mode == 'auto':
        source_task_request(user_source_task)

    return user_source_task


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

    user_source_task = db.session.query(SourceTask).filter_active().filter_by(uid=uid).first()
    if not user_source_task:
        return render_ext('base.html',
            message = ("User task not found: {0}".format(name), 'danger')
        )

    handler_dict = dict(user_source_task.handler.__dict__)
    handler_dict.pop('_sa_instance_state', None)

    cloud = get_cloud(user_source_task.source.user, user_source_task.source.provider)
    parsed = json.loads(cloud.extra_data)

    options = user_source_task.handler.options
    options['files'] = s.get('path')
    options['provider'] = s.get('provider')
    options['path_id'] = s.get('path_id')
    options['dbhome'] = user_source_task.source.user.home
    options['dbhome'] = parsed.get('access_token')
#   for key, value in options.items():
#       res = re.split('^{{ (.+) }}', value, 1)
#       if len(res) == 3:
#           _, code, value = res
#           options[key] = decode(code, value)

    for i in options:
        print(i, options[i])

    run_task_async.apply_async(args=[handler_dict, options])

    return redirect(get_next(back=True))


@app.route('/source_task/configure', methods=['GET', 'POST'])
@login_required
def user_source_task_configure():
    uid = request.values.get('uid')
    name = request.values.get('name')

    user_source_task = db.session.query(SourceTask).filter_active().filter_by(uid=uid).first()
    if not user_source_task:
        return render_ext('base.html',
            message = ("User task not found: {0}".format(name), 'danger')
        )

    return render_ext('db/user_source_task.html',
        source_task = user_source_task,
    )


@app.route('/source_task/append', methods=['GET', 'POST'])
@login_required
def user_source_task_append():
    sources = Source.query.filter_user(True).all()
    handlers = Handler.query.filter_user(True).all()
    form = AddSourceTaskForm(request.form, sources, handlers)

    message = ''
    if request.method == 'POST':
        if form.validate():
            source_task_create(form.user_source, form.user_handler, form.handling.data)
            message = "The task successfully added!"

        else:
            message = 'Invalid data!', 'danger'

    return render_ext('db/append_source_task.html',
        message = message,
        form = form,
    )


@app.route('/source_task/delete', methods=['GET', 'POST'])
@login_required
def user_source_task_delete():
    uid = request.values.get('uid')
    name = request.values.get('name')

    user_source_task = db.session.query(SourceTask).filter_active().filter_by(uid=uid).first()
    if not user_source_task:
        return render_ext('base.html',
            message = ("User task not found: {0}".format(name), 'danger')
        )

    user_source_task.deleted = True
    db.session.commit()

    return redirect(get_next(back=True))
