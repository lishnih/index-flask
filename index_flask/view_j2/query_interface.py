#!/usr/bin/env python
# coding=utf-8
# Stan 2012-02-25

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from collections import OrderedDict

from sqlalchemy import desc, distinct, func, or_
from sqlalchemy.sql import select

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


def qi_where(s, filter, columns_dict):
    for key, value in filter.items():
        if key in columns_dict:
            if value is None:
                s = s.where(columns_dict[key] == None)
            elif isinstance(value, basestring) or isinstance(value, int):
                s = s.where(columns_dict[key] == value)
            elif isinstance(value, float):
                s = s.where(columns_dict[key].like(value))
            else:
                condition, value = value
                if condition == '=' or condition == '==':
                    s = s.where(columns_dict[key] == value)
                elif condition == '!=':
                    s = s.where(columns_dict[key] != value)
                elif condition == '~':
                    s = s.where(columns_dict[key].like(value))
                elif condition == 'like':
                    s = s.where(columns_dict[key].like("%{0}%".format(value)))
                elif condition == '>':
                    s = s.where(columns_dict[key] > value)
                elif condition == '>=':
                    s = s.where(columns_dict[key] >= value)
                elif condition == '<':
                    s = s.where(columns_dict[key] < value)
                elif condition == '<=':
                    s = s.where(columns_dict[key] <= value)
    return s


def qi_query_count(user, db, tables, search=None, filter={}):
    if isinstance(tables, basestring):
        tables = tables,

    metadata = user_data.get_metadata(user, db)
    mtables = [metadata.tables.get(i) for i in tables]

    if None in mtables:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)

    session = user_data.get_session(user, db)



    query = session.query(*mtables)
#     full_rows_count = query.count()



    s_count = select(mtables, use_labels=True)
    mtable = mtables[0]
    full_rows_count = session.execute(s_count.select_from(mtable).count())
    full_rows_count = full_rows_count.first()[0]



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
             offset=0, limit=0, columns=[], distinct_column=[], plain=1):
    if isinstance(tables, basestring):
        tables = tables,
    if isinstance(sorting, basestring):
        sorting = sorting,
    if isinstance(columns, basestring):
        columns = columns,
    if isinstance(distinct_column, basestring):
        distinct_column = distinct_column,

    tables = [i for i in tables if i]
    sorting = [i for i in sorting if i]
    columns = [i for i in columns if i]
    distinct_column = [i for i in distinct_column if i]


    db_uri, session, metadata, relationships = user_data.get_db(user, db)


    # Список таблиц
    mtables = [metadata.tables.get(i) for i in tables]
    if None in mtables:
        return {}, [], "Не все таблицы доступны: {0!r}".format(tables)

    # Исходная таблица
    table1 = tables[0]
    mtable1 = mtables[0]

    # Список всех колонок + кеш
    names = []
    columns_dict = {}
    for mtable in mtables:
        for mcolumn in mtable.c:
            cname = "{0}.{1}".format(mcolumn.table.name, mcolumn.name)
            names.append(cname)
            columns_dict[cname] = mcolumn

    # Формируем список колонок для вывода
    mcolumns = []

    if distinct_column:
        for column in distinct_column:
            if column not in names:
                column = "{0}.{1}".format(table1, column)

            if column in names:
                mcolumns.append(distinct(columns_dict[column]))

    elif columns:
        for column in columns:
            if column not in names:
                column = "{0}.{1}".format(table1, column)

            if column in names:
                mcolumns.append(columns_dict[column])

    else:
        for i in mtables:
            mcolumns.extend(j for j in i.c if not j.foreign_keys and not j.primary_key and j.name[0] != '_')


    # Join для таблиц
    for i in range(len(tables) - 1):
        for j in mtables[i + 1].foreign_keys:
            if j.column.table == mtables[i]:
                mtable1 = mtable1.join(mtables[i+1], j.parent==j.column)
                break
        else:
            first, second = tables[i], tables[i+1]
            rel = relationships.get(first, {}).get(second)

            if rel:
                their, own = rel
                own = columns_dict["{0}.{1}".format(second, own)]
                their = columns_dict["{0}.{1}".format(first, their)]
                mtable1 = mtable1.join(mtables[i+1], own==their)

            else:
                return {}, [], "Таблицы не связаны: {0!r} {1!r}".format(first, second)


    # Дополнительные таблицы
    primarytables = []
    for i in range(len(tables)):
        for j in mtables[i].foreign_keys:
            primarytables.append(j.column.table.name)

    for i in relationships:
        if table1 in relationships[i]:
            primarytables.append(i)

    primarytables = [i for i in set(primarytables) if i not in tables]

    table = relationships.get(tables[-1], {})
    followedtables = table.keys() if table else []
    followedtables = [i for i in set(followedtables) if i not in tables]


    s = select(mcolumns, use_labels=True).select_from(mtable1)


    # Получаем кол-во всех записей
    if not distinct_column:   # !!!
        result = session.execute(s.count())
        full_rows_count = result.first()[0]
    else:
        full_rows_count = -1


    # Поиск по всем полям
    if search:
        search_str = "%{0}%".format(search)
        or_query = or_(*[mcolumn.like(search_str) for mcolumn in mcolumns])

        s = s.where(or_query)

    # или фильтр
    elif filter:
        for column, val in filter.items():
            if column not in names:
                column = "{0}.{1}".format(table1, column)
                filter.pop(column, None)

            if column in names:
                filter[column] = val

        s = qi_where(s, filter, columns_dict)


    # Получаем кол-во записей после фильтрации
    if not distinct_column:   # !!!
        result = session.execute(s.count())
        filtered_rows_count = result.first()[0]
    else:
        filtered_rows_count = -1


    # Сортировка
    for column in sorting:
        if isinstance(column, basestring):
            if column not in names:
                column = "{0}.{1}".format(table1, column)

            if column in names:
                s = s.order_by(columns_dict[column])
        else:
            column, directional = column

            if column not in names:
                column = "{0}.{1}".format(table1, column)

            if directional == 'desc':
                s = s.order_by(desc(columns_dict[column]))
            else:
                s = s.order_by(columns_dict[column])


    # Выборка
    s = s.offset(offset)
    if limit:
        s = s.limit(limit)


    # Получаем кол-во записей в выборке
    if not distinct_column:   # !!!
        result = session.execute(s.count())
        rows_count = result.first()[0]
    else:
        rows_count = -1


    # Получаем записи и поля
    if distinct_column:     # !!!
        names = [repr(column) for name, column in s._columns_plus_names]
    else:
        names = ["{0}.{1}".format(column.table.name, column.name) for name, column in s._columns_plus_names]
    result = session.execute(s)


    # Преобразуем в требуемый формат
    if plain:
        rows = [[j for j in i] for i in result.fetchall()]
    else:
        rows = [OrderedDict((zip(names, i))) for i in result.fetchall()]


    return dict(
        full_rows_count = full_rows_count,
        filtered_rows_count = filtered_rows_count,
        rows_count = rows_count,
        columns = names,
        primarytables = primarytables,
        followedtables = followedtables,
        query = unicode(s),
    ), rows, None
