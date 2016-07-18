#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-28

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os

from flask import request, render_template, jsonify, redirect, flash, abort

from flask_login import login_required
from flask_principal import Permission, RoleNeed

from .core.backwardcompat import *
from .core.dump_html import html
from .core.html_helpers import parse_input, parse_span, dye_red, dye_green
from .models import db, User, Group, Module
from .forms import RegistrationForm, AddGroupForm

from . import app, get_next


admin_permission = Permission(RoleNeed('admin'))


@app.route('/admin/')
@login_required
@admin_permission.require(403)
def admin():
    return render_template('admin/index.html',
             title = 'Admin page',
           )


@app.route('/admin/users')
@login_required
@admin_permission.require(403)
def admin_users():
    s = User.query
    total = s.count()

    users = s.all()
    names = [i.name for i in User.__table__.c]
    names.insert(0, '#')
#   rows = [[seq if i == '#' else user.__dict__.get(i) for i in names] for seq, user in enumerate(users, 1)]
    rows = []
    for seq, user in enumerate(users, 1):
        row = []
        for i in names:
            if i == '#':
                row.append('<i>{0}</i>'.format(seq))
            elif i == 'email':
                row.append('<a href="user/{0}">{0}</a>'.format(user.email))
            else:
                row.append(user.__dict__.get(i))

        rows.append(row)

    return render_template('admin/users.html',
             title = 'Users',
             names = names,
             rows = rows,
             total = total,
           )


@app.route('/admin/user/<email>')
@login_required
@admin_permission.require(403)
def admin_user(email):
    user = User.query.filter_by(email=email).first()

    names = [i.name for i in User.__table__.c]
    rows = [[user.__dict__.get(i) for i in names]]

    return render_template('admin/users.html',
             title = 'User',
             names = names,
             rows = rows,
           )


@app.route('/admin/groups')
@login_required
@admin_permission.require(403)
def admin_groups():
    s = Group.query
    total = s.count()

    groups = s.all()
    names = [i.name for i in Group.__table__.c]
    names.insert(0, '#')
#   rows = [[seq if i == '#' else groups.__dict__.get(i) for i in names] for seq, user in enumerate(groups, 1)]
    rows = []
    for seq, group in enumerate(groups, 1):
        row = []
        for i in names:
            if i == '#':
                row.append('<i>{0}</i>'.format(seq))
            elif i == 'name':
                row.append('<a href="group/{0}">{0}</a>'.format(group.name))
            else:
                row.append(group.__dict__.get(i))

        rows.append(row)

    return render_template('admin/users.html',
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

    return render_template('admin/users.html',
             title = 'Group',
             names = names,
             rows = rows,
           )


@app.route('/admin/users_groups', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def admin_users_groups():
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

    names = ['#', 'id', 'email']
    for group in groups:
        names.append(group.name)

    rows = []
    for seq, user in enumerate(users, 1):
        row = ['<i>{0}</i>'.format(seq), user.id, user.email]

        for group in groups:
            row.append(parse_input('', group in user.groups, 'toggle_record',
                id = user.id,
                group = group.name,
            ))

        rows.append(row)

    return render_template('admin/users.html',
             title = 'User groups',
             names = names,
             rows = rows,
           )


@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def admin_add_user():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            email = form.email.data,
            username = form.username.data,
            name = form.name.data,
            company = form.company.data,
            password = form.password.data,
        )
        db.session.add(user)
        db.session.commit()

        flash('User added!')

        return redirect(get_next('/admin/'))

    return render_template('user/register.html',
             title = 'Registering new user',
             form = form,
             next = request.args.get('next', '/admin/'),
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

        return redirect(get_next('/admin/'))

    return render_template('admin/add_group.html',
             title = 'Appending new group',
             form = form,
           )


@app.route('/admin/modules', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def admin_modules():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'delete_record':
            id = request.form.get('id')
            if id:
                module = Module.query.filter_by(id=id).first()
                if module:
                    db.session.delete(module)

        elif action == 'toggle_record':
            id = request.form.get('id')
            checked = request.form.get('checked')
            checked = True if checked == 'true' else False
            if id:
                module = Module.query.filter_by(id=id).first()
                if module:
                    if checked:
                        if module.active:
                            return jsonify(result='rejected', message='The module is already active.')

                    else:
                        if not module.active:
                            return jsonify(result='rejected', message='The module is already disabled.')

                    module.active = checked

        if action:
            db.session.commit()

        return jsonify(result='accepted', message=action)

    s = Module.query
    total = s.count()

    modules = s.all()
    names = [i.name for i in Module.__table__.c]
    names.insert(0, '#')
#   rows = [[seq if i == '#' else module.__dict__.get(i) for i in names] for seq, module in enumerate(modules, 1)]
    rows = []
    for seq, module in enumerate(modules, 1):
        row = []
        for i in names:
            if i == '#':
                row.append('<i>{0}</i>'.format(seq))
            elif i == 'active':
                row.append(parse_input('', module.active, 'toggle_record',
                    id = module.id,
                ))
            else:
                row.append(module.__dict__.get(i))

        # Delete
        row.append(parse_span('', '[ x ]', 'delete_record',
            id = module.id,
        ))
        # On the disk
        fl = os.path.isfile(os.path.join(app.root_path, module.folder, "{0}.py".format(module.name)))
        row.append(dye_green('Yes') if fl else dye_red('No'))

        rows.append(row)

    names.append('Delete')
    names.append('On the disk')

    return render_template('admin/modules.html',
             title = 'App modules',
             names = names,
             rows = rows,
             total = total,
           )
