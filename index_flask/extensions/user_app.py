#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-12

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import re
from datetime import datetime

from flask import request, render_template, redirect, url_for, flash

from flask_login import login_required, current_user

from wtforms import Form, BooleanField, StringField, validators

from ..core.backwardcompat import *
from ..core.dump_html import html
from ..models import db, User
from .. import app, require_ext, admin_permission


##### Model #####

relationship_user_app = db.Table('rs_user_app',
    db.Column('_user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('_app_id', db.Integer, db.ForeignKey('app.id'), nullable=False),
    db.Column('token', db.String, nullable=False, default=''),
    db.Column('sticked', db.Boolean, nullable=False, default=True),
    db.Column('options', db.PickleType, nullable=False, default={}),
    db.Column('created', db.DateTime),    # !!!
    db.PrimaryKeyConstraint('_user_id', '_app_id'))


class App(db.Model):          # Rev. 2016-07-12
    __tablename__ = 'app'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime)

    def __init__(self, name, description=''):
        self.name = name.lower()
        self.description = description
        self.created = datetime.utcnow()

User.ext_apps = db.relationship('App', backref='user', secondary=relationship_user_app)

db.create_all()


##### Form #####

class AddAppForm(Form):
    name = StringField('Name *', [
        validators.Length(min=6, max=40)
    ])
    description = StringField('Description')

    def validate(self):
        validated = True

        rv = Form.validate(self)
        if not rv:
            validated = False

        if not re.match('^[A-Za-z][\w.]*$', self.name.data):
            self.name.errors.append('All characters in the string must be alphanumeric or dot with underline')
            validated = False

        app = App.query.filter_by(name=self.name.data).first()
        if app:
            self.name.errors.append('App with the same name already registered')
            validated = False

        return validated


##### Interface #####

def get(app):
    if current_user.is_anonymous:
        return {}

    app = App.query.filter_by(name=group).first()

    if checked:
        if group in user.groups:
            return jsonify(result='rejected', message='The user is already in the group.')
    k


##### Routes #####

@app.route('/app<int:id>', methods=['GET', 'POST'])
@login_required
def view_app(id):
    form = AddAppForm(request.form)
    if request.method == 'POST' and form.validate():
        app = App(
            name = form.name.data,
            description = form.description.data,
        )
        db.session.add(app)
        db.session.commit()

        flash('App created!')

    app = App.query.filter_by(id=id).first()
    if app:
        if 'attach' in request.args:
            current_user.ext_apps.append(app)
            db.session.commit()
            return redirect(url_for('view_app', id=id))

    else:
        flash('App is not created yet!')

        p_admin = admin_permission.can()
        return render_template('ext_user_app/add_app.html',
             title = '',
             p_admin = p_admin,
             form = form,
#            debug = html(table_info),
        )

    attached = app in current_user.ext_apps
    k

    return render_template('ext_user_app/index.html',
               title = 'Options',
               attached = attached,
#              debug = html(table_info),
           )
