#!/usr/bin/env python
# coding=utf-8
# Stan 2019-01-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json

from flask import request, redirect, flash

from flask_login import login_required, current_user

from sqlalchemy.sql import select, func, text, column, table, and_

from ..app import app, db
from ..core_flask.functions import get_next
from ..core_flask.render_response import render_ext
from ..forms.user_task import AddUserTaskForm
from ..models.handler import Handler
from ..models.source import Source
from ..models.user_task import UserTask

from ..tools.run_task import run_task
from ..tools.send_csv import send_csv


# ===== Interface =====

def get_cloud(user, provider_name):
    usersocialauth = table('social_auth_usersocialauth')
    user_id = column('user_id')
    provider = column('provider')
    s = select(['*'], and_(user_id == user.id, provider == provider_name), usersocialauth)

    res = db.session.execute(s)

    return res.fetchone()


def task_run(user_task, user=None):
    if not user:
        user = current_user

    if user_task.type == 2:
        options = dict(user_task.options)
        options['dbhome'] = user.home

        send_csv_async.delay(user.id, options)
#       send_csv_async(user.id, options)

        return 'Sending CSV...'

    # user_task.type == 1
    if user_task.handler:
        handler_dict = dict(user_task.handler.__dict__)
        handler_dict.pop('_sa_instance_state', None)
        options = dict(user_task.handler.options)

    else:
        handler_dict = {}
        options = {}

    options.update(user_task.options)

    app.logger.info(str(user_task.source))
    if user_task.source:
        cloud = get_cloud(user_task.source.user, user_task.source.provider)
        parsed = json.loads(cloud.extra_data)

        options['dbhome'] = user_task.source.user.home
        options['files'] = user_task.source.path
        options['provider'] = user_task.source.provider.replace('-oauth2', '')
        options['path_id'] = user_task.source.path_id
        options['access_token'] = parsed.get('access_token')

    else:
        options['dbhome'] = user.home

    app.logger.info(str(handler_dict))
    app.logger.info(str(options))

    run_task_async.apply_async(args=[handler_dict, options])

    return 'Running...'


# ===== Routes =====

@app.route('/user_task/run')
@login_required
def user_task_run():
    uid = request.values.get('uid')
    name = request.values.get('name')

    user_task = db.session.query(UserTask).filter_by(uid=uid).filter_user(True).first()
    if not user_task:
        return render_ext('base.html',
            message = ("User task not found: {0}".format(name), 'danger')
        )

    msg = task_run(user_task)
    flash(msg)

    return redirect(get_next(back=True))
