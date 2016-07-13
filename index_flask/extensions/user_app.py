#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-12

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import re, hashlib, random
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.sql import select

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
    db.Column('attached', db.DateTime),
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

def init_rs_user_app(current_user, app):
    s = relationship_user_app.update(values=dict(
          attached = datetime.utcnow(),
          token = suit_code(current_user.id, app.id),
        )).where(
          and_(relationship_user_app.c._user_id == current_user.id,
          relationship_user_app.c._app_id == app.id)
        )
    res = db.session.execute(s)
    db.session.commit()

def get_token(user, app):
#   rnd = datetime.now().strftime("%Y%m%d%H%M%S.%f")
    rnd = random.randint(0, 100000000000000)
    return hashlib.md5("{0}_{1}_{2}".format(rnd, user, app)).hexdigest()

def suit_code(user, app):
    double = True
    while double:
        token = get_token(user, app)
#         double = RS_App.query.filter_by(token=token).first()

        s = select('*').select_from(relationship_user_app).\
              where(relationship_user_app.c.token==token)
        res = db.session.execute(s)
        double = res.first()

    return token


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

            init_rs_user_app(current_user, app)
            return redirect(url_for('view_app', id=id))

    else:
        flash('App is not created yet!')

        p_admin = admin_permission.can()
        return render_template('extensions/user_app/add_app.html',
                 title = '',
                 p_admin = p_admin,
                 form = form,
#                debug = html(table_info),
               )

    s = select('*').select_from(relationship_user_app).where(
          and_(relationship_user_app.c._user_id == current_user.id,
          relationship_user_app.c._app_id == app.id)
        )

    res = db.session.execute(s)
    user_app = res.first()
    if user_app:
        user_app = dict(user_app.items())

        options = user_app.pop('options')
    else:
        options = {}

    names = [i.name for i in App.__table__.c]
    row = [app.__dict__.get(i) for i in names]
    app = dict((zip(names, row)))

    return render_template('extensions/user_app/index.html',
             title = 'Options',
             app = app,
             user_app = user_app,
             options = options,
#            debug = html(table_info),
           )
