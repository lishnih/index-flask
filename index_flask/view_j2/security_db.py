#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-13

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import g


def user_table_iter(userid):
    for table in g.metadata.tables.keys():
        yield table


def get_user_table_data(userid, table):
    if table in g.metadata.tables.keys():
        return g.metadata.tables.get(table)
#     else:
#         return 'No such table!'
