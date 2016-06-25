#!/usr/bin/env python
# coding=utf-8
# Stan 2012-02-25

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from sqlalchemy import desc, distinct, func, or_

from .. import user_data


def qi_columns_list(user, db, tables, fullnames_option = 1):
    if isinstance(tables, basestring):
        tables = tables,

    metadata = user_data.get_metadata(user, db)
    mtables = [metadata.tables.get(i) for i in tables]

    if None in mtables:
        return None

    columns_list = []
    for mtable in mtables:
        for column in mtable.c:
            cname = "{0}.{1}".format(column.table.name, column.name) \
                    if fullnames_option else column.name
            columns_list.append(cname)

    return columns_list


def qi_columns_dict(user, db, tables, fullnames_option = 1):
    if isinstance(tables, basestring):
        tables = tables,

    metadata = user_data.get_metadata(user, db)
    mtables = [metadata.tables.get(i) for i in tables]

    if None in mtables:
        return None

    columns_dict = {}
    for mtable in mtables:
        for column in mtable.c:
            cname = "{0}.{1}".format(column.table.name, column.name) \
                    if fullnames_option else column.name
            columns_dict[cname] = column

    return columns_dict


def qi_query_filter(query, filter, columns_dict):
    for key, value in filter.items():
        if key in columns_dict:
            if value == None:
                query = query.filter(columns_dict[key] == None)
            elif isinstance(value, basestring) or isinstance(value, int):
                query = query.filter(columns_dict[key] == value)
            elif isinstance(value, float):
                query = query.filter(columns_dict[key].like(value))
            else:
                condition, value = value
                if condition == '=' or condition == '==':
                    query = query.filter(columns_dict[key] == value)
                elif condition == '!=':
                    query = query.filter(columns_dict[key] != value)
                elif condition == '~':
                    query = query.filter(columns_dict[key].like(value))
                elif condition == 'like':
                    query = query.filter(columns_dict[key].like("%{0}%".format(value)))
                elif condition == '>':
                    query = query.filter(columns_dict[key] > value)
                elif condition == '>=':
                    query = query.filter(columns_dict[key] >= value)
                elif condition == '<':
                    query = query.filter(columns_dict[key] < value)
                elif condition == '<=':
                    query = query.filter(columns_dict[key] <= value)
    return query


def qi_query_count(user, db, tables, search=None, filter={}):
    if isinstance(tables, basestring):
        tables = tables,

    metadata = user_data.get_metadata(user, db)
    mtables = [metadata.tables.get(i) for i in tables]

    if None in mtables:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)

    session = user_data.get_session(user, db)
    query = session.query(*mtables)

    full_rows_count = query.count()

    columns_dict = qi_columns_dict(user, db, tables)
    if columns_dict is None:
        return {}, "Колонки не определены: {0!r}".format(db)

    if search:
        search_str = "%{0}%".format(search)
        or_query = or_(*[columns_dict[key].like(search_str) for key in columns_dict])
        query = query.filter(or_query)

    if filter:
        query = qi_query_filter(query, filter, columns_dict)

    filtered_rows_count = query.count()

    return dict(
        full_rows_count     = full_rows_count,
        filtered_rows_count = filtered_rows_count,
#       rows_count          = rows_count,
        query = unicode(query)
    ), None


def qi_query_column(user, db, tables, column, operand, search=None, filter={}):
    if isinstance(tables, basestring):
        tables = tables,

    metadata = user_data.get_metadata(user, db)
    mtables = [metadata.tables.get(i) for i in tables]

    if None in mtables:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)

    session = user_data.get_session(user, db)
    query = session.query(*mtables)

    columns_dict = qi_columns_dict(user, db, tables)
    if columns_dict is None:
        return {}, "Колонки не определены: {0!r}".format(db)

    if column not in columns_dict:
        return {}, "Заданной колонки не существует: {0}".format(column)

    if   operand == 'sum':
        query = session.query(func.sum(columns_dict[column]).label('sum'))
    elif operand == 'max':
        query = session.query(func.max(columns_dict[column]).label('max'))
    elif operand == 'min':
        query = session.query(func.min(columns_dict[column]).label('min'))
    else:
        return {}, "Не задана функция: {0}".format(operand)

    if search:
        search_str = "%{0}%".format(search)
        or_query = or_(*[columns_dict[key].like(search_str) for key in columns_dict])
        query = query.filter(or_query)

    if filter:
        query = qi_query_filter(query, filter, columns_dict)

    val = query.all()[0][0]

    return dict(
        val = val,
        query = unicode(query)
    ), None


def qi_query_sum(user, db, tables, column, search=None, filter={}):
    if isinstance(tables, basestring):
        tables = tables,

    metadata = user_data.get_metadata(user, db)
    mtables = [metadata.tables.get(i) for i in tables]

    if None in mtables:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)

    session = user_data.get_session(user, db)
    query = session.query(*mtables)

    columns_dict = qi_columns_dict(user, db, tables)
    if columns_dict is None:
        return {}, "Колонки не определены: {0!r}".format(db)

    if column not in columns_dict:
        column = "{0}.{1}".format(tables[0], column)

    if column not in columns_dict:
        return {}, "Заданной колонки не существует: {0}".format(column)

    query = session.query(func.sum(columns_dict[column]).label('sum'))

    if search:
        search_str = "%{0}%".format(search)
        or_query = or_(*[columns_dict[key].like(search_str) for key in columns_dict])
        query = query.filter(or_query)

    if filter:
        query = qi_query_filter(query, filter, columns_dict)

    column_sum = query.all()[0].sum

    return dict(
        sum = column_sum,
        query = unicode(query)
    ), None


def qi_query(user, db, tables, search=None, filter={}, sorting=[],
             offset=0, limit=0, columns=None, distinct_column=None):
    if isinstance(tables, basestring):
        tables = tables,

    metadata = user_data.get_metadata(user, db)
    mcolumns = []

    columns_dict = qi_columns_dict(user, db, tables)
    if columns_dict is None:
        return {}, [], "Колонки не определены: {0!r}".format(db)

    if distinct_column:
        if distinct_column not in columns_dict:
            distinct_column = "{0}.{1}".format(tables[0], distinct_column)

        mcolumns.append(distinct(columns_dict[distinct_column]))
        if not columns:
            columns = [distinct_column]

    # !!! нет проверок
    if columns:
        for column in columns:
            if column != distinct_column:
                mcolumns.append(columns_dict[column])

    # !!! нет проверок
    else:
        for table in tables:
            mcolumns.append(metadata.tables.get(table))

#   if None in mcolumns:
#       return {}, [], "Некоторые таблицы недоступны: {0!r}".format(tables)

    session = user_data.get_session(user, db)
    query = session.query(*mcolumns)

    full_rows_count = query.count()

    for column in sorting:
        if isinstance(column, basestring):
            if column not in columns_dict:
                column = "{0}.{1}".format(tables[0], column)

            query = query.order_by(columns_dict[column])
        else:
            column, directional = column

            if column not in columns_dict:
                column = "{0}.{1}".format(tables[0], column)

            if directional == 'desc':
                query = query.order_by(desc(columns_dict[column]))
            else:
                query = query.order_by(columns_dict[column])

    if search:
        search_str = "%{0}%".format(search)
        or_query = or_(*[columns_dict[key].like(search_str) for key in columns_dict])
        query = query.filter(or_query)

    if filter:
        for key, val in filter.items():
            if key not in columns_dict:
                filter.pop(key, None)
                filter["{0}.{1}".format(tables[0], key)] = val

        query = qi_query_filter(query, filter, columns_dict)

    filtered_rows_count = query.count()

    rows = query.slice(offset, offset + limit) if limit > 0 else \
           query.offset(offset)
    rows_count = rows.count()

    th_list = []
    for column_description in query.column_descriptions:
        th_list.append(column_description['name'])
#       th_list.append(column_description['expr'].element.name)

    td_list = [[i for i in row] for row in rows]

    return dict(
        full_rows_count     = full_rows_count,
        filtered_rows_count = filtered_rows_count,
        rows_count          = rows_count,
        columns = th_list,
        query = unicode(query)
    ), td_list, None
