#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import re
import math

from flask import escape

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import select, func, join, column, text, desc, and_

from .parse_multi_form import parse_multi_form


# Здесь же маскируются выводимые значения
def row_iter(names, row, seq=None):
    for i in names:
        yield i, escape(getattr(row, i))

    yield "_seq", seq


def get_names(session, sql):
    s = select(['*']).select_from(text("({0})".format(sql))).limit(0)
    res = session.execute(s)
    return res.keys()


def get_rows_dt(session, sql, datatables_values):
    start = datatables_values.get('start', '')
    length = datatables_values.get('length', '')

    start = int(start) if start.isdigit() else 0
    length = int(length) if length.isdigit() else limit_default

    requested_params = parse_multi_form(datatables_values)  # columns, order, search

    column_params = requested_params.get('columns', {})
    column_names = dict([(i, column_params.get(i, {}).get('data')) for i in column_params.keys()])
    column_searchables = dict([(i, column_params.get(i, {}).get('searchable')) for i in column_params.keys()])
    column_searchables = [column_names.get(k) for k, v in column_searchables.items() if v == 'true']

    search_params = requested_params.get('search', {})
    search = search_params.get('value')
    regex = search_params.get('regex')

    criterion = or_(*[column(i).like("%{0}%".format(search)) for i in column_searchables]) \
        if search else None

    order_params = requested_params.get('order', {})
    order = []
    for i in sorted(order_params.keys()):
        column_sort_dict = order_params.get(i)
        column_id = int(column_sort_dict.get('column', ''))
        sort_dir = column_sort_dict.get('dir', '')
        sort_column = column_names.get(column_id)
        if sort_column:
            c = desc(column(sort_column)) if sort_dir == 'desc' else column(sort_column)
            order.append(c)

#                 debug_column_params = str(column_params),
#                 debug_column_names = str(column_names),
#                 debug_column_searchables = str(column_searchables),
#                 debug_search_params = str(search_params),
#                 debug_order_params = str(order_params),

    s = select(['*']).select_from(text("({0})".format(sql)))
    total = session.execute(s.count()).scalar()

    if criterion is None:
        filtered = total
    else:
        s = s.where(criterion)
        filtered = session.execute(s.count()).scalar()

    if order:
        s = s.order_by(*order)

    if start and start < filtered:
        s = s.offset(start)
    if length:
        s = s.limit(length)

    res = session.execute(s)
    names = res.keys()
    rows = [dict(row_iter(names, row, start+i)) for i, row in enumerate(res.fetchall(), 1)]

    return names, rows, total, filtered, s
