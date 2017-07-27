#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-02, 2017-07-23

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import json, time
from datetime import datetime

from flask import request, render_template, jsonify, redirect, url_for, flash

from flask_login import login_required, current_user

from sqlalchemy import Column, Integer, Float, String, DateTime, PickleType, ForeignKey, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import select, text

from wtforms import Form, TextAreaField, StringField, SelectField, HiddenField, validators

from ..core.backwardcompat import *
from ..core.db import init_db, get_db_list
from ..core.dump_html import html

from ..a import app


##### Models #####

Base = declarative_base()
if sys.version_info >= (3,):
    class aStr():
        def __str__(self):
            return self.__unicode__()
else:
    class aStr():
        def __str__(self):
            return self.__unicode__().encode('utf-8')


# String = String(length=255)


class Obj(Base, aStr):        # Rev. 2016-07-27
    __tablename__ = 'data_obj'

    id = Column(Integer, primary_key=True)
    _user_id = Column(Integer)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False, default='')
    obj = Column(PickleType)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, name, obj_data, description=''):
        self._user_id = user_id
        self.name = name
        self.description = description
        self.obj = obj_data


class Sheet(Base, aStr):      # Rev. 2016-07-27
    __tablename__ = 'data_sheet'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _user_id = Column(Integer)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False, default='')
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, name, sheet_data, description=''):
        self._user_id = user_id
        self.name = name
        self.description = description

        for y, row in enumerate(sheet_data, 1):
            for x, value in enumerate(row, 1):
                if value is not None:
                    cell = Cell(x, y, value)
                    self.data_cell.append(cell)


class List(Base, aStr):       # Rev. 2016-07-27
    __tablename__ = 'data_list'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _user_id = Column(Integer)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False, default='')
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, name, list_data, description=''):
        self._user_id = user_id
        self.name = name
        self.description = description

        for y, value in enumerate(list_data, 1):
            if value is not None:
                cell = Cell(0, y, value)
                self.data_cell.append(cell)


class Cell(Base, aStr):       # Rev. 2016-07-26
    __tablename__ = 'data_cell'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _sheet_id = Column(Integer, ForeignKey('data_sheet.id'))
    _sheet = relationship(Sheet, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))
    _list_id = Column(Integer, ForeignKey('data_list.id'))
    _list = relationship(List, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    x = Column(Integer, nullable=False, default=0)
    y = Column(Integer, nullable=False, default=0)
    value = Column(String, nullable=False)

    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value


class Dict(Base, aStr):       # Rev. 2016-07-27
    __tablename__ = 'data_dict'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _user_id = Column(Integer)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False, default='')
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, name, dict_data, description=''):
        self._user_id = user_id
        self.name = name
        self.description = description

        for key, value in dict_data.items():
            cell = KCell(key, value)
            self.data_kcell.append(cell)


class KCell(Base, aStr):      # Rev. 2016-07-26
    __tablename__ = 'data_kcell'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _dict_id = Column(Integer, ForeignKey('data_dict.id'))
    _dict = relationship(Dict, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    key = Column(String, nullable=False)
    value = Column(String)

    def __init__(self, key, value):
        self.key = key
        self.value = value


##### Interface #####

def get(session, current_user, type, id=None, name='default'):
    if current_user.is_anonymous:
        return

    if type == 'obj':
        s = session.query(Obj)
        if id:
            s = s.filter(Obj._user_id==current_user.id, Obj.id==id)
        else:
            s = s.filter(Obj._user_id==current_user.id, Obj.name==name)
        row = s.first()

    elif type == 'sheet':
        s = session.query(Sheet)
        if id:
            s = s.filter(Sheet._user_id==current_user.id, Sheet.id==id)
        else:
            s = s.filter(Sheet._user_id==current_user.id, Sheet.name==name)
        row = s.first()

    elif type == 'list':
        s = session.query(List)
        if id:
            s = s.filter(List._user_id==current_user.id, List.id==id)
        else:
            s = s.filter(List._user_id==current_user.id, List.name==name)
        row = s.first()

    elif type == 'dict':
        s = session.query(Dict)
        if id:
            s = s.filter(Dict._user_id==current_user.id, Dict.id==id)
        else:
            s = s.filter(Dict._user_id==current_user.id, Dict.name==name)
        row = s.first()

    else:
        raise Exception, 'Wrong type {0}'.type(type)

    return row


def get_obj(session, current_user, id=None, name='default'):
    if current_user.is_anonymous:
        return

    s = session.query(Obj)
    if id:
        s = s.filter(Obj._user_id==current_user.id, Obj.id==id)
    else:
        s = s.filter(Obj._user_id==current_user.id, Obj.name==name)
    row = s.first()
    if row:
        return row.obj


def get_sheet(session, current_user, id=None, name='default'):
    if current_user.is_anonymous:
        return

    s = session.query(Sheet)
    if id:
        s = s.filter(Sheet._user_id==current_user.id, Sheet.id==id)
    else:
        s = s.filter(Sheet._user_id==current_user.id, Sheet.name==name)
    row = s.first()
    if row:
        s = select([text('max(x)'), text('max(y)')]).select_from(Cell)
        s = s.where(Cell._sheet_id==row.id)
        res = session.execute(s)
        x, y = res.fetchone()
        sheet = [[None for i in range(x)] for i in range(y)]

        for cell in row.data_cell:
            sheet[cell.y-1][cell.x-1] = cell.value

        return sheet


def get_list(session, current_user, id=None, name='default'):
    if current_user.is_anonymous:
        return

    s = session.query(List)
    if id:
        s = s.filter(List._user_id==current_user.id, List.id==id)
    else:
        s = s.filter(List._user_id==current_user.id, List.name==name)
    row = s.first()
    if row:
        s = select([text('max(y)')]).select_from(Cell)
        s = s.where(Cell._list_id==row.id)
        res = session.execute(s)
        y = res.scalar()
        list = [None for i in range(y)]

        for cell in row.data_cell:
            list[cell.y-1] = cell.value

        return list


def get_dict(session, current_user, id=None, name='default'):
    if current_user.is_anonymous:
        return

    s = session.query(Dict)
    if id:
        s = s.filter(Dict._user_id==current_user.id, Dict.id==id)
    else:
        s = s.filter(Dict._user_id==current_user.id, Dict.name==name)
    row = s.first()
    if row:
        dict = {}
        for cell in row.data_kcell:
            dict[cell.key] = cell.value

        return dict


def set_obj(session, current_user, data, name='default'):
    if current_user.is_anonymous:
        return

    obj = get_obj(session, current_user, name=name)
    if not obj:
        obj = Obj(current_user.id, 'name', data)
        session.add(obj)
        session.commit()


def set_sheet(session, current_user, data, name='default'):
    if current_user.is_anonymous:
        return

    obj = get_sheet(session, current_user, name=name)
    if not obj:
        obj = Sheet(current_user.id, 'name', data)
        session.add(obj)
        session.commit()


def set_list(session, current_user, data, name='default'):
    if current_user.is_anonymous:
        return

    obj = get_list(session, current_user, name=name)
    if not obj:
        obj = List(current_user.id, 'name', data)
        session.add(obj)
        session.commit()


def set_dict(session, current_user, data, name='default'):
    if current_user.is_anonymous:
        return

    obj = get_dict(session, current_user, name=name)
    if not obj:
        obj = Dict(current_user.id, 'name', data)
        session.add(obj)
        session.commit()


# def update_obj(session, current_user, data, name='default'):
#     if current_user.is_anonymous:
#         return
#
#     s = session.query(Obj)
#     s = s.filter(Obj._user_id==current_user.id, Obj.name==name)
#     row = s.first()
#     if row:
#         row.obj = data
#         session.commit()


##### Forms #####

class DataForm(Form):
    db = HiddenField()

    examples = [
      ['', ''],
      ["""{\n"a": 1,\n"b": "text"\n}""", 'obj'],
      ["""[\n[11, 12, 13],\n[21, 22, "text"]\n]""", 'sheet'],
      ["""[\n11,\n12,\n"text"\n]""", 'list'],
      ["""{\n"a": 1,\n"b": "text"\n}""", 'dict'],
    ]
    example = SelectField('Example', choices=examples)

    input_data = TextAreaField('Input data')

    data_types = [[i, i] for i in [
        'obj', 'sheet', 'list', 'dict',
    ]]
    type = SelectField('Data type', choices=data_types)

    name = StringField('Name')


##### Views interface #####

def get_dbs_table(home, db=None):
    dbs_list = get_db_list(home)
    dbs_list = sorted(dbs_list)

    names = ['Databases', 'Info']
    dbs_table = [['<a href="{0}"><b><i>{1}</i></b></a>'.format(url_for('ext_user_data', db=dbname), dbname) if db == dbname else
                    '<a href="{0}">{1}</a>'.format(url_for('ext_user_data', db=dbname), dbname),
                  '<a href="{0}">{1}</a>'.format(url_for('views_db_info', db=dbname), '>'),
                ] for dbname in dbs_list]

    return names, dbs_table


def get_objects(session, metadata, db, user_id):
    obj = []

    mtable = metadata.tables.get('data_obj')
    s = select('*').select_from(mtable).where(mtable.c._user_id==user_id)
    res = session.execute(s)
    obj.append(
        [
          ['Name', 'Description'],
          [['<a href="{0}">{1}</a>'.format(url_for('ext_user_data_obj', db=db, id=i.id), i.name), i.description] for i in res.fetchall()],
          'Objects',
          '<a href="{0}">Add</a>'.format(url_for('ext_user_data_add', db=db, type='obj'))
        ]
    )

    mtable = metadata.tables.get('data_sheet')
    s = select('*').select_from(mtable).where(mtable.c._user_id==user_id)
    res = session.execute(s)
    obj.append(
        [
          ['Name', 'Description'],
          [['<a href="{0}">{1}</a>'.format(url_for('ext_user_data_sheet', db=db, id=i.id), i.name), i.description] for i in res.fetchall()],
          'Sheets',
          '<a href="{0}">Add</a>'.format(url_for('ext_user_data_add', db=db, type='sheet'))
        ]
    )

    mtable = metadata.tables.get('data_list')
    s = select('*').select_from(mtable).where(mtable.c._user_id==user_id)
    res = session.execute(s)
    obj.append(
        [
          ['Name', 'Description'],
          [['<a href="{0}">{1}</a>'.format(url_for('ext_user_data_list', db=db, id=i.id), i.name), i.description] for i in res.fetchall()],
          'Lists',
          '<a href="{0}">Add</a>'.format(url_for('ext_user_data_add', db=db, type='list'))
        ]
    )

    mtable = metadata.tables.get('data_dict')
    s = select('*').select_from(mtable).where(mtable.c._user_id==user_id)
    res = session.execute(s)
    obj.append(
        [
          ['Name', 'Description'],
          [['<a href="{0}">{1}</a>'.format(url_for('ext_user_data_dict', db=db, id=i.id), i.name), i.description] for i in res.fetchall()],
          'Dicts',
          '<a href="{0}">Add</a>'.format(url_for('ext_user_data_add', db=db, type='dict'))
        ]
    )

    return obj


##### Routes #####

@app.route("/user_data/", methods=["GET", "POST"])
@app.route("/user_data/<db>/")
@login_required
def ext_user_data(db=None):
    input_data = request.values.get('input_data')

    if input_data:
#         try:
        db = request.values.get('db')
        name = request.values.get('name')
        type = request.values.get('type')
#       format = request.values.get('format')
        obj = json.loads(input_data)

        db_uri, session, metadata = init_db(current_user.home, db)
        if not db_uri:
            return jsonify(result='error', message="База данных не существует: {0}".format(db))

        if get(session, current_user, type, name=name):
            name = "{0}_{1}".format(name, int(time.time()))

        if type == 'obj':
            obj = Obj(current_user.id, name, obj)

        elif type == 'sheet':
            obj = Sheet(current_user.id, name, obj)

        elif type == 'list':
            obj = List(current_user.id, name, obj)

        elif type == 'dict':
            obj = Dict(current_user.id, name, obj)

        else:
            return jsonify(result='error', message="Unknown type data")

        session.add(obj)
        session.commit()

#         except Exception as e:
#             return jsonify(result='error', message=e.message)

        return jsonify(result='ok', message='')

    else:
        names, dbs_table = get_dbs_table(current_user.home, db)
        html = ''
        obj = []

        if db:
            db_uri, session, metadata = init_db(current_user.home, db)
            if not db_uri:
                flash("База данных не существует: {0}".format(db), 'error')
                return render_template('p/empty.html')

            if 'yes' in request.values:
                Base.metadata.create_all(session.bind)
                metadata.reflect()

            table = 'data_cell'
            if table in metadata.tables:
                obj = get_objects(session, metadata, db, current_user.id)

            else:
                flash("Таблицы не созданы! Создать?", 'info')
                html = '<ul><li><a href="?yes">Yes</a></li><li><a href="..">No</a></li></ul>'

        return render_template('db/index.html',
                 title = 'Databases',
                 names = names,
                 rows = dbs_table,
                 html = html,
                 obj = obj,
               )


@app.route("/user_data/<db>/drop")
@login_required
def ext_user_data_drop(db):
    names, dbs_table = get_dbs_table(current_user.home, db)
    html = ''
    obj = []

    if db:
        db_uri, session, metadata = init_db(current_user.home, db)
        if not db_uri:
            flash("База данных не существует: {0}".format(db), 'error')
            return render_template('p/empty.html')

        if 'yes' in request.values:
            Base.metadata.drop_all(session.bind)
            return redirect(url_for('ext_user_data'))

        table = 'data_cell'
        if table in metadata.tables:
            flash("Таблицы данных будут безвозвратно удалены! Вы уверены?", 'error')
            html = '<ul><li><a href="?yes">Yes</a></li><li><a href="..">No</a></li></ul>'

        else:
            html = "<i>Таблицы данных отсутствуют!</i>"

    return render_template('db/index.html',
             title = 'Databases',
             names = names,
             rows = dbs_table,
             html = html,
             obj = obj,
           )


@app.route("/user_data/<db>/obj/<id>")
@login_required
def ext_user_data_obj(db, id):
    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    obj = get_obj(session, current_user, id)

    return render_template('p/empty.html',
             text = json.dumps(obj),
           )


@app.route("/user_data/<db>/sheet/<id>")
@login_required
def ext_user_data_sheet(db, id):
    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    rows = get_sheet(session, current_user, id)

    return render_template('dump_table.html',
             rows = rows,
           )


@app.route("/user_data/<db>/list/<id>")
@login_required
def ext_user_data_list(db, id):
    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    rows = get_list(session, current_user, id)
    rows = [[i] for i in rows]

    return render_template('dump_table.html',
             rows = rows,
           )


@app.route("/user_data/<db>/dict/<id>")
@login_required
def ext_user_data_dict(db, id):
    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    obj = get_dict(session, current_user, id)

    return render_template('dump_dict.html',
             obj = obj,
           )


@app.route("/user_data/<db>/add")
@login_required
def ext_user_data_add(db):
    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    form = DataForm(request.values)
    form.db.data = db
    form.name.data = 'default'
    request_url = url_for('ext_user_data')

    type = request.values.get('type')
    if type:
        form.type.data = type

    return render_template('data/add.html',
             title = 'Data',
             form = form,
             action = request_url,
           )


@app.route("/user_data/<db>/set_test")
@login_required
def ext_user_data_set_test(db):
    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    dobj = dict(
        a = [
              [None, 12,   13, 14, 15, None],
              [  21, 22, None, 24, 25, None],
              [  31, 32,   33, 34, 35, None],
            ],
        b = 10,
    )
    dobj = Obj(current_user.id, 'name', dobj)
    session.add(dobj)

    dobj = Obj(current_user.id, 'null', None)
    session.add(dobj)

    dsheet = [
               [None, 12,   13, 14, 15, None],
               [  21, 22, None, 24, 25, None],
               [  31, 32,   33, 34, 35, None],
             ]
    dsheet = Sheet(current_user.id, 'name', dsheet)
    session.add(dsheet)

    dlist = [11, 12, None, 14, 15, None, None]
    dlist = List(current_user.id, 'name', dlist)
    session.add(dlist)

    ddict = dict(
        a = 1,
        b = 2,
        c = 3,
        d = None,
    )
    ddict = Dict(current_user.id, 'name', ddict)
    session.add(ddict)

    session.commit()

    return 'proceeded'
