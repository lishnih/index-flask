#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from sqlalchemy import create_engine, MetaData


def initDb(db_uri):
    engine = create_engine(db_uri)
    metadata = MetaData(engine, reflect=True)

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

    return engine, metadata, relationships
