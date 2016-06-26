#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os.path

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker


def initDb(home, dbname):
    db_uri = "{0}:///{1}/{2}.sqlite".format('sqlite', home, dbname)

    engine = create_engine(db_uri)
    metadata = MetaData(engine, reflect=True)

    session = scoped_session(sessionmaker())
    session.configure(bind=engine)

    tables = {}
    relationships = dict()

    for table in sorted(metadata.tables.keys()):
        table = metadata.tables.get(table)
        tables[table.name] = []
        for column in table.c:
            tables[table.name].append(column.name)

            if column.name[0:1] == '_':
                try:
                    x, first_table, unique_key = column.name.split('_', 2)
                    if first_table not in relationships:
                        relationships[first_table] = dict()
                    relationships[first_table][table.name] = [unique_key, column.name]
                except ValueError:
                    pass

    return db_uri, session, metadata, relationships


def getDbList(home):
    db_dict = {}
    try:
        ldir = os.listdir(home)
    except OSError:
        pass
    else:
        for name in ldir:
            fullname = os.path.join(home, name)
            if os.path.isfile(fullname):
                filename, ext = os.path.splitext(name)
                if ext == '.sqlite':
                    db_dict[filename] = fullname

    return db_dict
