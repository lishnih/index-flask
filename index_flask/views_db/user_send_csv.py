#!/usr/bin/env python
# coding=utf-8
# Stan 2019-01-18

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, redirect, flash

from flask_login import login_required, current_user

from ..app import app, db
from ..core_flask.render_response import render_ext
from ..extensions.celery_send_csv_task import send_csv_async
from ..models.user_task import UserTask


@app.route("/user_task/send_csv")
@login_required
def utask_send_csv():
    uid = request.values.get('uid')
    name = request.values.get('name')

    utask = db.session.query(UserTask).filter_by(uid=uid).filter_user(True).first()
    if not utask:
        return render_ext('base.html',
            message = ("User task not found: {0}".format(name), 'danger')
        )

    options = dict(utask.options)
    options['dbhome'] = current_user.home

    send_csv_async.delay(current_user.id, options)

    flash('Sending CSV...')
    return redirect(get_next(back=True))
