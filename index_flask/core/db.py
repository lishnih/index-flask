#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import re
import math

from sqlalchemy import create_engine, MetaData, func, join, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import select, text


dbname_ptrn = re.compile("^[\w\-+=\.,\(\)\[\]\{\}';]+$")

def init_db(home, dbname, create=False):
    result = dbname_ptrn.match(dbname)
    if result:
        home = os.path.expanduser(home)
        filename = os.path.join(home, "{0}.sqlite".format(dbname))
        if os.path.isfile(filename) or create:
            db_uri = "{0}:///{1}".format('sqlite', filename)

            engine = create_engine(db_uri, convert_unicode=True)
            metadata = MetaData(engine, reflect=True)

            db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))

            return db_uri, db_session, metadata

    return None, None, None


def get_dbs_list(home):
    try:
        ldir = os.listdir(home)
    except OSError:
        pass
    else:
        for name in ldir:
            dbname, ext = os.path.splitext(name)
            if ext == '.sqlite':
                yield dbname


def get_columns(mtables):
    if isinstance(mtables, (list, tuple)):
        for mtable in mtables:
            for c in mtable.c:
                yield c
    else:
        for c in mtables.c:
            yield c


def get_columns_names(mtables):
    if isinstance(mtables, (list, tuple)):
        for mtable in mtables:
            for c in mtable.c:
                yield "{0}.{1}".format(c.table.name, c.name)
    else:
        for c in mtables.c:
            yield c.name


def get_column(mtables, column_name):
    column_list = column_name.split('.')
    column_list.insert(0, '')
    table, column = column_list[-2:]

    if column:
        if isinstance(mtables, (list, tuple)):
            for mtable in mtables:
                if mtable.name == table:
                    return mtable.c.get(column)
        else:
            return mtables.c.get(column)


def get_primary_tables(metadata, tablename):
    mtable = metadata.tables.get(tablename)
    for key in mtable.foreign_keys:
        yield key.parent, key.column.table


def get_relative_tables(metadata, tablename):
    for (table, column), fk_list in metadata._fk_memos.items():
        if table == tablename:
            for i in fk_list:
                yield i.parent.table.name


def get_count(query):
    return query.with_entities(func.count()).scalar()


def get_rows_plain(session, sql, offset=0, limit=None, criterion=None, order=None, plain=1):
    s = select(['*']).select_from(text("({0})".format(sql)))
    total = session.execute(s.count()).scalar()

    if criterion:
        s = s.where(text(' and '.join(criterion)))
        filtered = session.execute(s.count()).scalar()
    else:
        filtered = total
    if order:
        s = s.order_by(text(', '.join(order)))
    if offset and offset < filtered:
        s = s.offset(offset)
    if limit:
        s = s.limit(limit)

    res = session.execute(s)
    names = res.keys()

    if plain:
#       rows = [i for i in res.fetchall()]
        rows = [[j for j in i] for i in res.fetchall()]
    else:
        rows = [dict(i.items()) for i in res.fetchall()]

    shown = len(rows)

    pages = int(math.ceil(filtered / limit)) if limit else 0
    page = int(math.floor(offset / limit)) + 1 if limit else 0
    if page > pages:
        page = 0

    return names, rows, total, filtered, shown, page, pages, s


def get_rows_model(model, offset=0, limit=None, criterion=None, order=None, plain=1):
    s = model.query
    total = s.count()

    if criterion:
        s = s.filter(*criterion)
        filtered = s.count()
    else:
        filtered = total
    if order:
        s = s.order_by(*order)
    if offset and offset < filtered:
        s = s.offset(offset)
    if limit:
        s = s.limit(limit)

    res = s.all()
    names = [i.name for i in model.__table__.c]

    if plain:
        rows = [[row.__dict__.get(i) for i in names] for row in res]
    else:
        rows = [dict((i, row.__dict__.get(i)) for i in names)]

    shown = len(rows)

    pages = int(math.ceil(filtered / limit)) if limit else 0
    page = int(math.floor(offset / limit)) + 1 if limit else 0
    if page > pages:
        page = 0

    return names, rows, total, filtered, shown, page, pages, s


def get_rows_base(session, mtable, offset=0, limit=None, criterion=None, order=None, plain=1):
    s = select(['*'], mtable)
    s_count = select([func.count()], mtable)
    total = session.execute(s_count).scalar()

    if criterion:
        s = s.where(and_(*criterion))
        s_count = s_count.where(and_(*criterion))
        filtered = session.execute(s_count).scalar()
    else:
        filtered = total
    if order:
        s = s.order_by(*order)
    if offset and offset < filtered:
        s = s.offset(offset)
    if limit:
        s = s.limit(limit)

    res = session.execute(s)
    names = res.keys()

    if plain:
        rows = [[j for j in i] for i in res.fetchall()]
    else:
        rows = [dict(i.items()) for i in res.fetchall()]

    shown = len(rows)

    pages = int(math.ceil(filtered / limit)) if limit else 0
    page = int(math.floor(offset / limit)) + 1 if limit else 0
    if page > pages:
        page = 0

    return names, rows, total, filtered, shown, page, pages, s


def get_rows_ext(session, mtables, offset=0, limit=None, criterion=None, order=None, plain=1):
    query = session.query(*mtables)

    for i in mtables:
        clauses = [key.column == key.parent for key in i.foreign_keys if key.column.table in mtables]
        l = len(clauses)
        if l == 1:
            query = query.join(i, *clauses)
        elif l > 1:
            query = query.join(i, and_(*clauses))

    total = query.count()

    if criterion:
        query = query.filter(*criterion)
        filtered = query.count()
    else:
        filtered = total
    if order:
        query = query.order_by(*order)
    if offset and offset < filtered:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    res = session.execute(query)
    names = res.keys()

    if plain:
        rows = [[j for j in i] for i in res.fetchall()]
    else:
        rows = [dict(i.items()) for i in res.fetchall()]

    shown = len(rows)

    pages = int(math.ceil(filtered / limit)) if limit else 0
    page = int(math.floor(offset / limit)) + 1 if limit else 0
    if page > pages:
        page = 0

    return names, rows, total, filtered, shown, page, pages, query
