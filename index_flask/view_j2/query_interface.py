#!/usr/bin/env python
# coding=utf-8
# Stan 2012-02-25

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from sqlalchemy import desc, distinct, func, or_

from ..user_data import get_session, get_table_data


def qi_columns_list(user, db, tables, fullnames_option = 0):
    if isinstance(tables, basestring):
        tables = tables,

    columns_list = []

    for table in tables:
        mtable = get_table_data(user, db, table)
        if mtable is not None:
            for column in mtable.c:
                cname = "{0}.{1}".format(column.table.name, column.name) \
                        if fullnames_option else column.name
                columns_list.append(cname)

    print(columns_list)
    return columns_list


def qi_columns_dict(user, db, tables):
    if isinstance(tables, basestring):
        tables = tables,

    columns_dict = dict()

    # Для первой таблицы предусматриваем короткие названия колонок
#   table = tables[0]
#   columns_list = qi_columns_list(user, db, table)
#   if columns_list:
#       mtable = get_table_data(user, db, table)
#       for column in columns_list:
#           columns_dict[column] = mtable.c[column]

    for table in tables:

        # В этом странном коде мы убираем db_tag из имени колонки
        if '.' in table:
            table_list = table.split('.')
            table_brief = table_list[1]
        else:
            table_brief = table

        columns_list = qi_columns_list(user, db, table)
        if columns_list:
            mtable = get_table_data(user, db, table)
            for column in columns_list:
                full_column = "{0}.{1}".format(table_brief, column)
                columns_dict[full_column] = mtable.c[column]

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

    classes = []
    for table in tables:
        classes.append(get_table_data(user, db, table))

    if None in classes:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)

    session = get_session(user, db)
    query = session.query(*classes)

    full_rows_count = query.count()

    columns_dict = qi_columns_dict(user, db, tables)

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

    classes = []
    for table in tables:
        classes.append(get_table_data(user, db, table))

    if None in classes:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)

    session = get_session(user, db)
    query = session.query(*classes)

    columns_dict = qi_columns_dict(user, db, tables)
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

    classes = []
    for table in tables:
        classes.append(get_table_data(user, db, table))

    if None in classes:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)

    session = get_session(user, db)
    query = session.query(*classes)

    columns_dict = qi_columns_dict(user, db, tables)
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

    columns_dict = qi_columns_dict(user, db, tables)

    classes = []

    if distinct_column:
        classes.append(distinct(columns_dict[distinct_column]))
        if not columns:
            columns = [distinct_column]

        pre = tables[0].split('.')[0]
        tablename = columns_dict[distinct_column].table.name
        distinct_table = "{0}.{1}".format(pre, tablename)
#       additional_tables = list(tables)
#       if distinct_table in additional_tables:
#           additional_tables.remove(distinct_table)

    # !!! нет проверок
    if columns:
        for column in columns:
            if column != distinct_column:
                classes.append(columns_dict[column])

#       if not distinct_column:
#           additional_tables = tables[1:]

    # !!! нет проверок
    else:
        for table in tables:
            classes.append(get_table_data(user, db, table))

#       additional_tables = tables[1:]

        if None in classes:
            return {}, [], "Некоторые таблицы недоступны: {0!r}".format(tables)

    session = get_session(user, db)
    query = session.query(*classes)

#   if additional_tables:
#       for table in additional_tables:
#           query = query.join(get_table_data(user, db, table))

    full_rows_count = query.count()

    for column in sorting:
        if isinstance(column, basestring):
            query = query.order_by(columns_dict[column])
        else:
            column, directional = column
            if directional == 'desc':
                query = query.order_by(desc(columns_dict[column]))
            else:
                query = query.order_by(columns_dict[column])

    if search:
        search_str = "%{0}%".format(search)
        or_query = or_(*[columns_dict[key].like(search_str) for key in columns_dict])
        query = query.filter(or_query)

    if filter:
        query = qi_query_filter(query, filter, columns_dict)

    filtered_rows_count = query.count()

    rows = query.slice(offset, offset + limit) if limit > 0 else \
           query.offset(offset)
    rows_count = rows.count()

    th_list = []
    for column_description in query.column_descriptions:
#       th_list.append(column_description['name'])
        th_list.append(unicode(column_description['expr']).replace('.', '<br />'))

    td_list = [[i for i in row] for row in rows]
#   for row in rows:
#       tr = []
#       for label in row._labels:
#           tr.append(row.__getattribute__(label))
#       td_list.append(tr)

    return dict(
        full_rows_count     = full_rows_count,
        filtered_rows_count = filtered_rows_count,
        rows_count          = rows_count,
        columns = th_list,
        query   = unicode(query)
    ), td_list, None
