#!/usr/bin/env python
# coding=utf-8
# Stan 2012-02-25

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

# from collections import OrderedDict

from sqlalchemy import desc, distinct, func, or_
from sqlalchemy.sql import select

from ..core.db import get_primary_tables, get_relative_tables

from ..app import require_ext


def qi_columns_list(user, db, tables, fullnames_option=1):
    if isinstance(tables, basestring):
        tables = tables,

    user_db = require_ext('user_db')
    if not user_db:
        return None

    metadata = user_db.get_metadata(user, db)
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


def qi_columns_dict(user, db, tables, fullnames_option=1):
    if isinstance(tables, basestring):
        tables = tables,

    user_db = require_ext('user_db')
    if not user_db:
        return None

    metadata = user_db.get_metadata(user, db)
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

    user_db = require_ext('user_db')
    if not user_db:
        return None

    db_uri, session, metadata = user_db.get_db(user, db)
    if not db_uri:
        return {}, "БД не существует: {0}".format(db)

    mtables = [metadata.tables.get(i) for i in tables]

    if None in mtables:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)


    query = session.query(*mtables)
#     full_rows_count = query.count()


    s_count = select(mtables, use_labels=True)
    mtable = mtables[0]
    full_rows_count = session.execute(s_count.select_from(mtable).count()).scalar()


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

    user_db = require_ext('user_db')
    if not user_db:
        return None

    db_uri, session, metadata = user_db.get_db(user, db)
    if not db_uri:
        return {}, "БД не существует: {0}".format(db)

    mtables = [metadata.tables.get(i) for i in tables]

    if None in mtables:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)

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

    user_db = require_ext('user_db')
    if not user_db:
        return None

    db_uri, session, metadata = user_db.get_db(user, db)
    if not db_uri:
        return {}, "БД не существует: {0}".format(db)

    mtables = [metadata.tables.get(i) for i in tables]

    if None in mtables:
        return {}, "Некоторые таблицы недоступны: {0!r}".format(tables)

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
             offset=0, limit=0, columns=[], distinct_columns=[], plain=1):
    if isinstance(tables, basestring):
        tables = tables,
    if isinstance(sorting, basestring):
        sorting = sorting,
    if isinstance(columns, basestring):
        columns = columns,
    if isinstance(distinct_columns, basestring):
        distinct_columns = distinct_columns,

    tables = [i for i in tables if i]
    sorting = [i for i in sorting if i]
    columns = [i for i in columns if i]
    distinct_columns = [i for i in distinct_columns if i]


    links = {}
    for i in range(len(tables)):
        table = tables[i]
        if ':' in table:
            table, link = table.split(':')
            tables[i] = table
            links[link] = table


    user_db = require_ext('user_db')
    if not user_db:
        return None

    db_uri, session, metadata = user_db.get_db(user, db)
    if not db_uri:
        return {}, [], "Нет такой БД: {0}".format(db)


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

    if distinct_columns:
        for column in distinct_columns:
            if column not in names:
                column = "{0}.{1}".format(table1, column)

            if column in names:
                if mcolumns:
                    mcolumns.append(columns_dict[column])
                else:
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
        first, second = tables[i], tables[i+1]
        if links.get(first) == second:
            for j in mtables[i].foreign_keys:
                if j.column.table == mtables[i+1]:
                    # j.parent - ссылка на другую таблицу
                    # j.column - первичный ключ
                    mtable1 = mtable1.join(mtables[i+1], j.parent==j.column)
                    break

            else:
                return {}, [], "Таблицы не связаны: {0!r} {1!r}".format(first, second)

        else:
            for j in mtables[i + 1].foreign_keys:
                if j.column.table == mtables[i]:
                    # j.parent - ссылка на другую таблицу
                    # j.column - первичный ключ
                    mtable1 = mtable1.join(mtables[i+1], j.parent==j.column)
                    break

            else:
                return {}, [], "Таблицы не связаны: {0!r} {1!r}".format(first, second)


    # Дополнительные таблицы
    primary_tables = []
    for i in range(len(tables)):
        for j in mtables[i].foreign_keys:
            primary_tables.append(j.column.table.name)

    primary_tables = [i for i in set(primary_tables) if i not in tables]


    relative_tables = get_relative_tables(metadata, table1)
    relative_tables = [i for i in set(relative_tables) if i not in tables]


    s = select(mcolumns, use_labels=True).select_from(mtable1)


    # Получаем кол-во всех записей
    if not distinct_columns:   # !!!
        full_rows_count = session.execute(s.count()).scalar()
    else:
        query = session.query(*mcolumns)
        full_rows_count = query.count()

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
    if not distinct_columns:   # !!!
        filtered_rows_count = session.execute(s.count()).scalar()
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
    if not distinct_columns:   # !!!
        rows_count = session.execute(s.count()).first()
    else:
        rows_count = -1


    # Получаем записи и поля
    if distinct_columns:     # !!!
        names = [repr(column) for name, column in s._columns_plus_names]
    else:
        names = ["{0}.{1}".format(column.table.name, column.name) for name, column in s._columns_plus_names]
    result = session.execute(s)


    # Преобразуем в требуемый формат
    if plain:
        rows = [[j for j in i] for i in result.fetchall()]
    else:
        rows = [dict(i.items()) for i in result.fetchall()]
#       rows = [OrderedDict(i.items()) for i in result.fetchall()]


    return dict(
        full_rows_count = full_rows_count,
        filtered_rows_count = filtered_rows_count,
        rows_count = rows_count,
        columns = names,
        primary_tables = primary_tables,
        relative_tables = relative_tables,
        query = unicode(s),
    ), rows, None
