#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-28

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from flask import request, jsonify, redirect, flash
from jinja2 import Markup, escape

from flask_login import login_required
from flask_principal import Permission, RoleNeed

from ..app import app, db
from ..core.functions import get_next
from ..core.html_helpers import parse_input, parse_span
from ..core.load_modules import is_loaded
from ..core.render_response import render_ext
from ..forms.group import AddGroupForm
from ..models.group import Group
from ..models.user import User


# ===== Roles =====

admin_permission = Permission(RoleNeed('admin'))


# ===== Routes =====

@app.route('/admin/groups')
@login_required
@admin_permission.require(403)
def admin_groups():
    s = Group.query
    groups = s.all()
    total = s.count()

    names = [i.name for i in Group.__table__.c]
    rows = []
    for group in groups:
        row = []
        for i in names:
            if i == 'name':
                row.append(Markup('<a href="group/{0}">{0}</a>'.format(escape(group.name))))
            else:
                row.append(group.__dict__.get(i))

        rows.append(row)

    return render_ext('base.html',
             title = 'Groups',
             names = names,
             rows = rows,
             total = total,
           )


@app.route('/admin/group/<name>')
@login_required
@admin_permission.require(403)
def admin_group(name):
    group = Group.query.filter_by(name=name).first()

    names = [i.name for i in Group.__table__.c]
    rows = [[group.__dict__.get(i) for i in names]]

    return render_ext('base.html',
             title = 'Group',
             names = names,
             rows = rows,
           )


@app.route('/admin/user_groups', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def admin_user_groups():
    if request.method == 'POST':
        action = request.form.get('action')
        result = 'omitted'
        message = ''

        if action == 'toggle_record':
            id = request.form.get('id')
            group = request.form.get('group')
            checked = request.form.get('checked')
            checked = True if checked == 'true' else False
            if id:
                user = User.query.filter_by(id=id).first()
                group = Group.query.filter_by(name=group).first()
                if user and group:
                    if checked:
                        if group in user.groups:
                            return jsonify(action=action, result='rejected', message='The user is already in the group.')

                        user.groups.append(group)
                        result = 'accepted'

                    else:
                        if group not in user.groups:
                            return jsonify(action=action, result='rejected', message='The user is not in the group.')

                        user.groups.remove(group)
                        result = 'accepted'

        return jsonify(action=action, result=result, message=message)

    users = User.query.all()
    groups = Group.query.all()
    total = len(users)

    names = ['id', 'email']
    for group in groups:
        names.append(group.name)

    rows = []
    for user in users:
        row = [user.id, escape(user.email)]

        for group in groups:
            row.append(parse_input('', group in user.groups, 'toggle_record',
                id = user.id,
                group = group.name,
            ))

        rows.append(row)

    return render_ext('admin/table_unsafe.html',
             title = 'User groups',
             names = names,
             rows = rows,
             total = total,
           )


@app.route('/admin/add_group', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def admin_add_group():
    form = AddGroupForm(request.form)
    if request.method == 'POST' and form.validate():
        group = Group(
            name = form.name.data,
            description = form.description.data,
        )
        db.session.add(group)
        db.session.commit()

        flash('Group added!')
        return redirect(get_next('admin'))

    return render_ext('admin/add_group.html',
             title = 'Appending new group',
             form = form,
           )
