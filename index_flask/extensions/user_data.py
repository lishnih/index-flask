#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-02, 2017-07-23

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import json, time
from datetime import datetime

from flask import request, render_template, jsonify, redirect, url_for, flash
from jinja2 import Markup, escape

from flask_login import login_required, current_user

from sqlalchemy import Column, Integer, Float, String, DateTime, PickleType, ForeignKey, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import select, text

from wtforms import Form, TextAreaField, StringField, SelectField, HiddenField, validators

from ..core.backwardcompat import *
from ..core.db import init_db, get_dbs_list
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


class Obj(Base, aStr):        # Rev. 2017-07-30
    __tablename__ = 'data_obj'

    id = Column(Integer, primary_key=True)
    _user_id = Column(Integer)

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False, default='')
    obj = Column(PickleType)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, name, data, description=''):
        self._user_id = user_id
        self.name = name
        self.description = description
        self.set(data)

    def set(self, data):
        self.obj = data

    def append(self, data):
        raise Exception('Inapplicable')

    def get(self):
        return self.obj


class Sheet(Base, aStr):      # Rev. 2017-07-30
    __tablename__ = 'data_sheet'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _user_id = Column(Integer)

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False, default='')
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, name, data, description=''):
        self._user_id = user_id
        self.name = name
        self.description = description
        self.set(data)

    def set(self, data):
        if self.data_cell:
            session = self._sa_instance_state.session
            for i in self.data_cell:
                session.delete(i)

        for y, row in enumerate(data, 1):
            for x, value in enumerate(row, 1):
                if value is not None:
                    cell = Cell(x, y, value)
                    self.data_cell.append(cell)

    def append(self, data):
        session = self._sa_instance_state.session

        s = select([text('max(y)')]).select_from(Cell)
        s = s.where(Cell._sheet_id==self.id)
        res = session.execute(s)
        y = res.scalar()

        for y, row in enumerate(data, y + 1):
            for x, value in enumerate(row, 1):
                if value is not None:
                    cell = Cell(x, y, value)
                    self.data_cell.append(cell)

    def get(self):
        session = self._sa_instance_state.session

        s = select([text('max(x)'), text('max(y)')]).select_from(Cell)
        s = s.where(Cell._sheet_id==self.id)
        res = session.execute(s)
        x, y = res.fetchone()

        sheet = [[]]
        if x and y:
            sheet = [[None for i in range(x)] for i in range(y)]

            for cell in self.data_cell:
                sheet[cell.y-1][cell.x-1] = cell.value

        return sheet


class List(Base, aStr):       # Rev. 2017-07-30
    __tablename__ = 'data_list'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _user_id = Column(Integer)

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False, default='')
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, name, data, description=''):
        self._user_id = user_id
        self.name = name
        self.description = description
        self.set(data)

    def set(self, data):
        if self.data_cell:
            session = self._sa_instance_state.session
            for i in self.data_cell:
                session.delete(i)

        for y, value in enumerate(data, 1):
            if value is not None:
                cell = Cell(0, y, value)
                self.data_cell.append(cell)

    def append(self, data):
        session = self._sa_instance_state.session

        s = select([text('max(y)')]).select_from(Cell)
        s = s.where(Cell._list_id==self.id)
        res = session.execute(s)
        y = res.scalar()

        for y, value in enumerate(data, y + 1):
            if value is not None:
                cell = Cell(0, y, value)
                self.data_cell.append(cell)

    def get(self):
        session = self._sa_instance_state.session

        s = select([text('max(y)')]).select_from(Cell)
        s = s.where(Cell._list_id==self.id)
        res = session.execute(s)
        y = res.scalar()
        list = [None for i in range(y)]

        for cell in self.data_cell:
            list[cell.y-1] = cell.value

        return list


class Cell(Base, aStr):       # Rev. 2017-07-26
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


class Dict(Base, aStr):       # Rev. 2017-07-30
    __tablename__ = 'data_dict'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _user_id = Column(Integer)

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False, default='')
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, name, data, description=''):
        self._user_id = user_id
        self.name = name
        self.description = description
        self.set(data)

    def set(self, data):
        if self.data_kcell:
            session = self._sa_instance_state.session
            for i in self.data_kcell:
                session.delete(i)

        for key, value in data.items():
            cell = KCell(key, value)
            self.data_kcell.append(cell)

    def append(self, data):
        session = self._sa_instance_state.session

        for key, value in data.items():
            s = session.query(KCell)
            s = s.filter(KCell._dict_id==self.id, KCell.key==key)
            res = s.all()
            for i in res:
                session.delete(i)

            kcell = KCell(key, value)
            self.data_kcell.append(kcell)

    def get(self):
        dict = {}
        for kcell in self.data_kcell:
            dict[kcell.key] = kcell.value

        return dict


class KCell(Base, aStr):      # Rev. 2017-07-26
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

def get_names(session, current_user, type):
    if current_user.is_anonymous:
        return []

    if type == 'obj':
        s = session.query(Obj.name)
        s = s.filter(Obj._user_id==current_user.id)

    elif type == 'sheet':
        s = session.query(Sheet.name)
        s = s.filter(Sheet._user_id==current_user.id)

    elif type == 'list':
        s = session.query(List.name)
        s = s.filter(List._user_id==List.id)

    elif type == 'dict':
        s = session.query(Dict.name)
        s = s.filter(Dict._user_id==Dict.id)

    else:
        raise Exception('Wrong type {0}'.type(type))

    rows = [i.name for i in s.all()]

    return rows


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
        raise Exception('Wrong type {0}'.type(type))

    return row


def save(session, current_user, type, data, name='default', mode='new'):
    if current_user.is_anonymous:
        return None, 'anonymous'

    obj = get(session, current_user, type, name=name)
    if obj:
        if mode == 'new':
            name = "{0}_{1}".format(name, int(time.time()))

        elif mode == 'rewrite':
            obj.set(data)
            return obj, 'data rewrited'

        elif mode == 'append':
            obj.append(data)
            return obj, 'data appended'

        else:
            raise Exception('Unknown mode {0}'.type(mode))

    if type == 'obj':
        obj = Obj(current_user.id, name, data)

    elif type == 'sheet':
        obj = Sheet(current_user.id, name, data)

    elif type == 'list':
        obj = List(current_user.id, name, data)

    elif type == 'dict':
        obj = Dict(current_user.id, name, data)

    else:
        raise Exception('Wrong type {0}'.type(type))

    session.add(obj)

    return obj, 'obj created'


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
    dbs_list = get_dbs_list(home)
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
          ['Name', 'Description', 'Created', 'Delete'],
          [[
              Markup('<a href="{0}">{1}</a>'.format(url_for('ext_user_data_obj', db=escape(db), id=i.id), escape(i.name))),
              i.description,
              i.created,
              Markup('<span class="a ia_delete_conf" data-action="delete" data-type="obj" data-id="{0}">></a>'.format(i.id))
           ] for i in res.fetchall()],
          'Objects',
          '<a href="{0}">Add</a>'.format(url_for('ext_user_data_add', db=db, type='obj'))
        ]
    )

    mtable = metadata.tables.get('data_sheet')
    s = select('*').select_from(mtable).where(mtable.c._user_id==user_id)
    res = session.execute(s)
    obj.append(
        [
          ['Name', 'Description', 'Created', 'Delete'],
          [[
              Markup('<a href="{0}">{1}</a>'.format(url_for('ext_user_data_sheet', db=escape(db), id=i.id), escape(i.name))),
              i.description,
              i.created,
              Markup('<span class="a ia_delete_conf" data-action="delete" data-type="sheet" data-id="{0}">></a>'.format(i.id))
           ] for i in res.fetchall()],
          'Sheets',
          '<a href="{0}">Add</a>'.format(url_for('ext_user_data_add', db=db, type='sheet'))
        ]
    )

    mtable = metadata.tables.get('data_list')
    s = select('*').select_from(mtable).where(mtable.c._user_id==user_id)
    res = session.execute(s)
    obj.append(
        [
          ['Name', 'Description', 'Created', 'Delete'],
          [[
              Markup('<a href="{0}">{1}</a>'.format(url_for('ext_user_data_list', db=escape(db), id=i.id), escape(i.name))),
              i.description,
              i.created,
              Markup('<span class="a ia_delete_conf" data-action="delete" data-type="list" data-id="{0}">></a>'.format(i.id))
           ] for i in res.fetchall()],
          'Lists',
          '<a href="{0}">Add</a>'.format(url_for('ext_user_data_add', db=db, type='list'))
        ]
    )

    mtable = metadata.tables.get('data_dict')
    s = select('*').select_from(mtable).where(mtable.c._user_id==user_id)
    res = session.execute(s)
    obj.append(
        [
          ['Name', 'Description', 'Created', 'Delete'],
          [[
              Markup('<a href="{0}">{1}</a>'.format(url_for('ext_user_data_dict', db=escape(db), id=i.id), escape(i.name))),
              i.description,
              i.created,
              Markup('<span class="a ia_delete_conf" data-action="delete" data-type="dict" data-id="{0}">></a>'.format(i.id))
           ] for i in res.fetchall()],
          'Dicts',
          '<a href="{0}">Add</a>'.format(url_for('ext_user_data_add', db=db, type='dict'))
        ]
    )

    return obj


##### Routes #####

@app.route("/user_data/", methods=["GET", "POST"])
@app.route("/user_data/<db>/", methods=["GET", "POST"])
@login_required
def ext_user_data(db=None):
    action = request.values.get('action')

    if action:
        if action == 'dbs_list':
            dbs_list = [i for i in get_dbs_list(current_user.home)]
            return jsonify(result='ok', rows=dbs_list)

        db = request.values.get('db', db)
        type = request.values.get('type')

        db_uri, session, metadata = init_db(current_user.home, db)
        if not db_uri:
            return jsonify(result='error', message="The database don't exists: {0}".format(db))

        if 'data_cell' not in metadata.tables:
            return jsonify(result='error', message="User data don't exist in the selected database!")

        if action == 'names_list':
            rows = get_names(session, current_user, type)
            return jsonify(result='ok', rows=rows)

        elif action == 'save':
#           try:
            name = request.values.get('name', 'default')
            mode = request.values.get('mode', 'new')
            data_json = request.values.get('data_json')
            data = json.loads(data_json)

            obj, status = save(session, current_user, type, data, name, mode)

            session.commit()

#           except Exception as e:
#               return jsonify(result='error', message=e.message)

            return jsonify(result='ok', id=obj.id, name=obj.name, status=status)

        elif action == 'delete':
            type = request.values.get('type')
            id = request.values.get('id')

            obj = get(session, current_user, type, id)

            if not obj:
                return jsonify(result='error', message="Object not found")

            session.delete(obj)
            session.commit()

            return jsonify(result='ok')

        else:
            return jsonify(result='error', message="Unknown action")

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
           )


@app.route("/user_data/<db>/obj/<id>")
@login_required
def ext_user_data_obj(db, id):
    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    obj = get(session, current_user, 'obj', id)

    return render_template('p/empty.html',
             text = json.dumps(obj.get()),
           )


@app.route("/user_data/<db>/sheet/<id>")
@login_required
def ext_user_data_sheet(db, id):
    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    sheet = get(session, current_user, 'sheet', id)

    return render_template('dump_table.html',
             rows = sheet.get(),
           )


@app.route("/user_data/<db>/list/<id>")
@login_required
def ext_user_data_list(db, id):
    db_uri, session, metadata = init_db(current_user.home, db)
    if not db_uri:
        flash("База данных не существует: {0}".format(db), 'error')
        return render_template('p/empty.html')

    list = get(session, current_user, 'list', id)
    rows = [[i] for i in list.get()]

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

    dict = get(session, current_user, 'dict', id)

    return render_template('dump_dict.html',
             obj = dict.get(),
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

    data = dict(
        a = [
              [None, 12,   13, 14, 15, None],
              [  21, 22, None, 24, 25, None],
              [  31, 32,   33, 34, 35, None],
            ],
        b = 10,
    )
    dobj = Obj(current_user.id, 'name', data)
    session.add(dobj)

    dobj = Obj(current_user.id, 'empty', None)
    session.add(dobj)

    dsheet = [
               [None, 12,   13, 14, 15, None],
               [  21, 22, None, 24, 25, None],
               [  31, 32,   33, 34, 35, None],
             ]
    dsheet = Sheet(current_user.id, 'name', dsheet)
    session.add(dsheet)

    data = [11, 12, None, 14, 15, None, None]
    dlist = List(current_user.id, 'name', data)
    session.add(dlist)

    data = dict(
        a = 1,
        b = 2,
        c = 3,
        d = None,
    )
    ddict = Dict(current_user.id, 'name', data)
    session.add(ddict)

    data = dict(
        b = 22,
        c = 23,
        d = None,
        e = 'new record',
    )
    ddict.append(data)

    session.commit()

    return 'proceeded'
