#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-22

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, redirect

from flask_login import login_required, current_user

from ..main import app, db
from ..core.functions import get_next
from ..core.render_response import render_ext
from ..models.handler import Handler


# ===== Routes =====

@app.route('/handlers')
@login_required
def user_handlers():
    handlers = db.session.query(Handler).filter(Handler.user == None).all()
    user_handlers = db.session.query(Handler).filter_user().all()

    return render_ext('db/user_handlers.html',
        handlers = handlers,
        user_handlers = user_handlers,
    )


@app.route('/handler/configure', methods=['GET', 'POST'])
@login_required
def user_handler_configure():
    uid = request.values.get('uid')
    name = request.values.get('name')

    user_handler = db.session.query(Handler).filter_user(public=True).filter_by(uid=uid).first()
    if not user_handler:
        return render_ext('base.html',
            message = ("Handler does not exist or deleted!", 'danger')
        )

    return render_ext('db/user_handler.html',
        handler = user_handler,
    )


@app.route('/handler/append', methods=['GET', 'POST'])
@login_required
def user_handler_append():
    return "under construction"


@app.route('/handler/append_test', methods=['GET', 'POST'])
@login_required
def user_handler_append_initial():
    handler = db.session.query(Handler).filter_by(name = 'scan_rfi').first()
    if handler:
        db.session.delete(handler)
    handler = db.session.query(Handler).filter_by(name = 'sheet_indexing').first()
    if handler:
        db.session.delete(handler)

    options = dict(
        profile = 'doc_rfi',
        opening = 'opening',
        entry = 'proceed',
        files_filter = '*.docx',
        dbname = 'scan_rfi',
        check = 'tick',
        tick = 'rev_1',
    )
    handler = Handler(
        user = current_user,
        name = 'scan_rfi',
        module = 'index_cloud.main',
        entry = 'main',
        key = 'options',
        options = options,
    )
    db.session.add(handler)

    options = dict(
        profile = 'sheet_indexing',
        opening = 'opening',
        entry = 'proceed',
        closing = 'closing',
        files_filter = '*.xlsx; *.xlsm',
        dbname = 'sheet_indexing',
        check = 'tick',
        tick = 'rev_1',
    )
    handler = Handler(
        user = current_user,
        name = 'sheet_indexing',
        module = 'index_cloud.main',
        entry = 'main',
        key = 'options',
        options = options,
    )
    db.session.add(handler)

    db.session.commit()

    return render_ext('base.html')


@app.route('/handler/delete', methods=['GET', 'POST'])
@login_required
def user_handler_delete():
    uid = request.values.get('uid')
    name = request.values.get('name')

    user_handler = db.session.query(Handler).filter_user().filter_by(uid=uid).first()
    if not user_handler:
        return render_ext('base.html',
            message = ("Handler does not exist or deleted!", 'danger')
        )

    user_handler.deleted = True
    db.session.commit()

    return redirect(get_next(back=True))
