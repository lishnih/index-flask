#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, re, math

from sqlalchemy import create_engine, MetaData, func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import select


dbname_ptrn = re.compile("^[\w\-+=\.,\(\)\[\]\{\}';]+$")


def initDb(home, dbname, create=False):
    result = dbname_ptrn.match(dbname)
    if result:
        filename = os.path.join(home, "{0}.sqlite".format(dbname))
        if os.path.isfile(filename) or create:
            db_uri = "{0}:///{1}".format('sqlite', filename)

            engine = create_engine(db_uri)
            metadata = MetaData(engine, reflect=True)

            session = scoped_session(sessionmaker())
            session.configure(bind=engine)

            return db_uri, session, metadata

    return None, None, None


def getDbList(home):
    try:
        ldir = os.listdir(home)
    except OSError:
        pass
    else:
        for name in ldir:
            dbname, ext = os.path.splitext(name)
            if ext == '.sqlite':
                yield dbname


def get_primary_tables(metadata, tablename):
    mtable = metadata.tables.get(tablename)
    for key in mtable.foreign_keys:
        yield key.column.table.name


def get_relative_tables(metadata, tablename):
    for (table, column), fk_list in metadata._fk_memos.items():
        if table == tablename:
            for i in fk_list:
                yield i.parent.table.name


def get_rows_base(session, mtable, offset, limit=None, criterion=None, order=None):
    s = select('*').select_from(mtable)
    s_count = select([func.count('*')]).select_from(mtable)
    total, = session.execute(s_count).first()
    if criterion:
        s = s.where(*criterion)
        s_count = s_count.where(*criterion)
        filtered, = session.execute(s_count).first()
    else:
        filtered = total
    if order:
        s = s.order_by(*order)
    s = s.offset(offset)
    if limit:
        s = s.limit(limit)
#   showed, = session.execute(s.count()).first()

    res = session.execute(s)
    names = res.keys()
#   rows = [i for i in res.fetchall()]
    rows = [[j for j in i] for i in res.fetchall()]
    showed = len(rows)

    pages = int(math.ceil(filtered / limit)) if limit else 0
    page = int(math.floor(offset / limit)) + 1 if limit else 0
    if page > pages: page = 0

    return names, rows, total, filtered, showed, page, pages, s
