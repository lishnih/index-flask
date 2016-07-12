#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-28

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import request, render_template, jsonify, redirect, flash, abort

from flask_login import current_user

from .core.backwardcompat import *
from .core.dump_html import html

from .models import db, User, Group, Module
from .forms import RegistrationForm, AddGroupForm

from . import app, admin_permission, get_next


@app.route('/admin/')
# @admin_permission.require(403)
def admin():
    if not admin_permission.can():
        abort(403)

    return render_template('admin/index.html',
             title = 'Admin page',
           )


@app.route('/admin/users')
@admin_permission.require(403)
def admin_users():
    users = User.query.all()

    names = [i.name for i in User.__table__.c]
#   rows = [[user.__dict__.get(i) for i in names] for user in users]
    rows = []
    for user in users:
        row = []
        for i in names:
            if i == 'email':
                row.append('<a href="user/{0}">{0}</a>'.format(user.email))
            else:
                row.append(user.__getattribute__(i))

        rows.append(row)

    return render_template('admin/users.html',
             title = 'Users',
             names = names,
             rows = rows,
           )


@app.route('/admin/user/<email>')
@admin_permission.require(403)
def admin_user(email):
    user = User.query.filter_by(email=email).first()

    names = [i.name for i in User.__table__.c]
    rows = [[user.__getattribute__(i) for i in names]]

    return render_template('admin/users.html',
             title = 'User',
             names = names,
             rows = rows,
           )


@app.route('/admin/groups')
@admin_permission.require(403)
def admin_groups():
    groups = Group.query.all()

    names = [i.name for i in Group.__table__.c]
#   rows = [[group.__dict__.get(i) for i in names] for group in groups]
    rows = []
    for group in groups:
        row = []
        for i in names:
            if i == 'name':
                row.append('<a href="group/{0}">{0}</a>'.format(group.name))
            else:
                row.append(group.__getattribute__(i))

        rows.append(row)

    return render_template('admin/users.html',
             title = 'Groups',
             names = names,
             rows = rows,
           )


@app.route('/admin/group/<name>')
@admin_permission.require(403)
def admin_group(name):
    group = Group.query.filter_by(name=name).first()

    names = [i.name for i in Group.__table__.c]
    rows = [[group.__getattribute__(i) for i in names]]

    return render_template('admin/users.html',
             title = 'Group',
             names = names,
             rows = rows,
           )


@app.route('/admin/users_groups', methods=['GET', 'POST'])
@admin_permission.require(403)
def admin_users_groups():
    if request.method == 'POST':
        id = request.form.get('id')
        group = request.form.get('group')
        checked = request.form.get('checked')
        checked = True if checked == 'true' else False

        user = User.query.filter_by(id=id).first()
        group = Group.query.filter_by(name=group).first()

        if checked:
            if group in user.groups:
                return jsonify(result='rejected', message='The user is already in the group.')

            user.groups.append(group)

        else:
            if group not in user.groups:
                return jsonify(result='rejected', message='The user is not in the group.')

            user.groups.remove(group)

        db.session.commit()

        return jsonify(result='accepted', message='Ok', checked=checked)

    users = User.query.all()
    groups = Group.query.all()

    names = ['id', 'email']
    for group in groups:
        names.append(group.name)

    rows = []
    for user in users:
        row = [user.id, user.email]

        for group in groups:
            checkbox = '<input class="user_group" type="checkbox" data-id="{0}" data-group="{1}" {2}>'
            row.append(checkbox.format(user.id, group.name, 'checked' if group in user.groups else ''))

        rows.append(row)

    return render_template('admin/users.html',
             title = 'User groups',
             names = names,
             rows = rows,
           )


@app.route('/admin/add_user', methods=['GET', 'POST'])
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
@admin_permission.require(403)
def admin_modules():
    if request.method == 'POST':
        id = request.form.get('id')
        checked = request.form.get('checked')
        checked = True if checked == 'true' else False

        module = Module.query.filter_by(id=id).first()

        if checked:
            if module.active:
                return jsonify(result='rejected', message='The module is already active.')

        else:
            if not module.active:
                return jsonify(result='rejected', message='The module is already disabled.')

        module.active = checked
        db.session.commit()

        return jsonify(result='accepted', message='Ok', checked=checked)

    modules = Module.query.all()

    names = [i.name for i in Module.__table__.c]

#   rows = [[module.__dict__.get(i) for i in names] for module in modules]
    rows = []
    for module in modules:
        row = []
        for i in names:
            if i == 'active':
                checkbox = '<input class="user_group" type="checkbox" data-id="{0}" {1}>'
                row.append(checkbox.format(module.id, 'checked' if module.active else ''))
            else:
                row.append(module.__getattribute__(i))

        rows.append(row)

    return render_template('admin/modules.html',
             title = 'App modules',
             names = names,
             rows = rows,
           )
