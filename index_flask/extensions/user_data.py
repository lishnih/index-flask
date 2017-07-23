#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-02, 2017-07-23

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import render_template, jsonify, url_for

from flask_login import login_required, current_user

from ..core.backwardcompat import *
from ..core.dump_html import html
from ..models import User

from ..a import app, db


##### Models #####

class Obj(db.Model):          # Rev. 2016-07-23
    __tablename__ = 'data_obj'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    _user = db.relationship(User, backref=db.backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False, default='')
    obj = db.Column(db.PickleType, nullable=False)

    def __init__(self, name, obj_data, description=''):
        self.name = name
        self.description = description
        self.obj = d


class Sheet(db.Model):        # Rev. 2017-07-23
    __tablename__ = 'data_sheet'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    _user = db.relationship(User, backref=db.backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False, default='')

    def __init__(self, name, sheet_data, description=''):
        self.name = name
        self.description = description

        for y, row in enumerate(sheet_data, 1):
            for x, value in enumerate(row, 1):
                obj = Cell(x, y, value)
                self.data_cell.append(obj)


class List(db.Model):         # Rev. 2017-07-23
    __tablename__ = 'data_list'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    _user = db.relationship(User, backref=db.backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False, default='')

    def __init__(self, name, list_data, description=''):
        self.name = name
        self.description = description

        for y, value in enumerate(list_data, 1):
            obj = Cell(0, y, value)
            self.data_cell.append(obj)


class Cell(db.Model):         # Rev. 2017-07-23
    __tablename__ = 'data_cell'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    _sheet_id = db.Column(db.Integer, db.ForeignKey('data_sheet.id'))
    _sheet = db.relationship(Sheet, backref=db.backref(__tablename__, cascade='all, delete, delete-orphan'))
    _list_id = db.Column(db.Integer, db.ForeignKey('data_list.id'))
    _list = db.relationship(List, backref=db.backref(__tablename__, cascade='all, delete, delete-orphan'))

    x = db.Column(db.Integer, nullable=False, default=0)
    y = db.Column(db.Integer, nullable=False, default=0)
    value = db.Column(db.String, nullable=False)

    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value


class Dict(db.Model):         # Rev. 2017-07-23
    __tablename__ = 'data_dict'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    _user = db.relationship(User, backref=db.backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False, default='')

    def __init__(self, name, dict_data, description=''):
        self.name = name
        self.description = description

        for key, value in dict_data.items():
            obj = KCell(key, value)
            self.data_kcell.append(obj)


class KCell(db.Model):        # Rev. 2017-07-23
    __tablename__ = 'data_kcell'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    _dict_id = db.Column(db.Integer, db.ForeignKey('data_dict.id'))
    _dict = db.relationship(Dict, backref=db.backref(__tablename__, cascade='all, delete, delete-orphan'))

    key = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value


db.create_all()


##### Interface #####

def get_objects(user):
    obj = [
            [
              ['Name', 'Description'],
              [['<a href="{0}">{1}</a>'.format(url_for('ext_user_data_obj', id=i.id), i.name), i.description] for i in user.data_obj],
              'Objects',
              '<a href="{0}">Add</a>'.format(url_for('ext_user_data_obj_add'))
            ],
            [
              ['Name', 'Description'],
              [['<a href="{0}">{1}</a>'.format(url_for('ext_user_data_sheet', id=i.id), i.name), i.description] for i in user.data_sheet],
              'Sheets',
              '<a href="{0}">Add</a>'.format(url_for('ext_user_data_sheet_add'))
            ],
            [
              ['Name', 'Description'],
              [['<a href="{0}">{1}</a>'.format(url_for('ext_user_data_list', id=i.id), i.name), i.description] for i in user.data_list],
              'Lists',
              '<a href="{0}">Add</a>'.format(url_for('ext_user_data_list_add'))
            ],
            [
              ['Name', 'Description'],
              [['<a href="{0}">{1}</a>'.format(url_for('ext_user_data_dict', id=i.id), i.name), i.description] for i in user.data_dict],
              'Dicts',
              '<a href="{0}">Add</a>'.format(url_for('ext_user_data_dict_add'))
            ],
          ]

    return obj


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

@app.route("/user_data/")
@app.route("/user_data/<name>")
@login_required
def ext_user_data():
    obj = get_objects(current_user)

    return render_template('db/index.html',
             title = 'Databases',
             obj = obj,
           )


@app.route("/user_data/set/")
@login_required
def ext_user_data_set():
    sheet = [
        [11, 12, 13, 14, 15],
        [21, 22, 23, 24, 25],
        [31, 32, 33, 34, 35],
    ]
    sheet = Sheet('123', sheet)
    current_user.data_sheet.append(sheet)

    db.session.add(sheet)
    db.session.commit()

    return 'proceeded'


@app.route("/user_data/obj/<id>")
@login_required
def ext_user_data_obj(id):
    return 'proceeded'


@app.route("/user_data/sheet/<id>")
@login_required
def ext_user_data_sheet(id):
    return 'proceeded'


@app.route("/user_data/list/<id>")
@login_required
def ext_user_data_list(id):
    return 'proceeded'


@app.route("/user_data/dict/<id>")
@login_required
def ext_user_data_dict(id):
    return 'proceeded'


@app.route("/user_data/obj/add")
@login_required
def ext_user_data_obj_add():
    return 'proceeded'


@app.route("/user_data/sheet/add")
@login_required
def ext_user_data_sheet_add():
    return 'proceeded'


@app.route("/user_data/list/add")
@login_required
def ext_user_data_list_add():
    return 'proceeded'


@app.route("/user_data/dict/add")
@login_required
def ext_user_data_dict_add():
    return 'proceeded'
