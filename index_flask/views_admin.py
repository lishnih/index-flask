#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-28

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import request, render_template, redirect, jsonify, flash, abort

from flask_login import current_user

from .core.backwardcompat import *
from .core.dump_html import html

from .models import db, User, Group
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

    names = []
    rows = []
    for user in users:
        if not names:
            names = [i.name for i in user.__table__.c]

        row = map(lambda x: user.__getattribute__(x), names)
        row[1] = '<a href="user/{0}">{0}</a>'.format(row[1])

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

    names = []
    rows = []

    if not names:
        names = [i.name for i in user.__table__.c]

    row = map(lambda x: user.__getattribute__(x), names)
    rows.append(row)

    return render_template('admin/users.html',
             title = 'User',
             names = names,
             rows = rows,
           )


@app.route('/admin/groups')
@admin_permission.require(403)
def admin_groups():
    groups = Group.query.all()

    names = []
    rows = []
    for group in groups:
        if not names:
            names = [i.name for i in group.__table__.c]

        row = map(lambda x: group.__getattribute__(x), names)
        row[1] = '<a href="group/{0}">{0}</a>'.format(row[1])

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

    names = []
    rows = []

    if not names:
        names = [i.name for i in group.__table__.c]

    row = map(lambda x: group.__getattribute__(x), names)
    rows.append(row)

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
        status = request.form.get('status')

        user = User.query.filter_by(id=id).first()
        group = Group.query.filter_by(name=group).first()

        if status == 'true':
            if group in user.groups:
                return jsonify(result='rejected', message='The user is already in the group.')

            user.groups.append(group)

        else:
            if group not in user.groups:
                return jsonify(result='rejected', message='The user is not in the group.')

            user.groups.remove(group)

        db.session.commit()

        return jsonify(result='accepted', message='Ok', status=status)

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
