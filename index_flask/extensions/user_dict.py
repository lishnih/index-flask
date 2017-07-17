#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-02

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask_login import login_required, current_user

from ..core.backwardcompat import *
from ..core.dump_html import html
from ..models import db, User

from .. import app


##### Models #####

class Dict(db.Model):         # Rev. 2016-07-02
    __tablename__ = 'dict'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String, nullable=False)
    obj = db.Column(db.PickleType, nullable=False)

    def __init__(self, name, d):
        self.name = name
        self.obj = d
#       self._user_id = user.id

User.ext_dicts = db.relationship('Dict', backref='user', lazy='dynamic')

db.create_all()


##### Interface #####

def get(current_user, name='default'):
    if current_user.is_anonymous:
        return {}

    obj = current_user.ext_dicts.filter_by(name=name).first()
    if obj:
        return obj.obj


def set(current_user, d, name='default'):
    if current_user.is_anonymous:
        return

    obj = current_user.ext_dicts.filter_by(name=name).first()
    if obj:
        obj.obj = d
    else:
        obj = Dict(name, d)
        current_user.ext_dicts.append(obj)

    db.session.commit()


def update(current_user, d, name='default'):
    if current_user.is_anonymous:
        return

    obj = current_user.ext_dicts.filter_by(name=name).first()
    if obj:
        new_d = obj.obj.copy()
        new_d.update(d)
        obj.obj = new_d
    else:
        obj = Dict(name, d)
        current_user.ext_dicts.append(obj)

    db.session.commit()


##### Routes #####

@app.route("/user_dict/")
@app.route("/user_dict/<name>")
@login_required
def ext_user_dict(name='default'):
    return html(get(current_user, name))


@app.route("/user_dict/set/")
@app.route("/user_dict/set/<name>")
@login_required
def ext_user_dict_set(name='default'):
    d = dict(a=1, b=20, c=300)
    set(current_user, d, name)
    return 'proceeded'


@app.route("/user_dict/update/")
@app.route("/user_dict/update/<name>")
@login_required
def ext_user_dict_update(name='default'):
    d = dict(b=40, d=200, e='300')
    update(current_user, d, name)
    return 'proceeded'
