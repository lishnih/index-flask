#!/usr/bin/env python
# coding=utf-8
# Stan 2012-02-06

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from .request_interface import *
from .response_interface import *
from .query_interface import *
from ..user_data import *


def set_default_db_action(user, request_items, response):
    db = ri_get_str(request_items, 'db')
    db = set_default_db(user, db)

    response['rows'] = [db]


def default_db_action(user, request_items, response):
    db = get_default_db(user)

    response['rows'] = [db]


def dbs_list_action(user, request_items, response):
    response['rows'] = [i for i in get_dbs_list(user)]


def tables_list_action(user, request_items, response):
    db = ri_get_str(request_items, 'db') or get_default_db(user)

    if not db:
        return response_with_message(response, "База данных не задана!", 'error')

    response['rows'] = [i for i in get_tables_list(user, db)]


def columns_list_action(user, request_items, response):
    db = ri_get_str(request_items, 'db') or get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
        return response_with_message(response, "База данных не задана!", 'error')

    if not tables[0]:
        return response_with_message(response, "Таблица не задана!", 'error')

    fullnames = ri_get_int(request_items, 'fullnames')

    columns_list = qi_columns_list(user, db, tables, fullnames)

    response['rows'] = columns_list


def table_count_action(user, request_items, response):
    db = ri_get_str(request_items, 'db') or get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
        return response_with_message(response, "База данных не задана!", 'error')

    if not tables[0]:
        return response_with_message(response, "Таблица не задана!", 'error')

    search = ri_get_str(request_items, 'search')    # Строка для поиска
    filter_dict = ri_get_obj(request_items, 'filter_json')

    query_params = dict(
        user = user,
        db = db,
        tables = tables,
        search = search,
        filter = filter_dict,
    )

    table_info, error = qi_query_count(**query_params)

    response.update(table_info)
    query_params['user'] = user.id
    response['query_params'] = query_params
    if error:
        response['error'] = error


def column_func_action(user, request_items, response):
    db = ri_get_str(request_items, 'db') or get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
        return response_with_message(response, "База данных не задана!", 'error')

    if not tables[0]:
        return response_with_message(response, "Таблица не задана!", 'error')

    column = ri_get_str(request_items, 'column')

    if not column:
        return response_with_message(response, "Колонка не задана!", 'error')

    operand = ri_get_str(request_items, 'func')

    if not func:
        return response_with_message(response, "Функция не задана!", 'error')

    search = ri_get_str(request_items, 'search')    # Строка для поиска
    filter_dict = ri_get_obj(request_items, 'filter_json')

    query_params = dict(
        user = user,
        db = db,
        tables  = tables,
        column  = column,
        operand = operand,
        search  = search,
        filter  = filter_dict,
    )

    table_info, error = qi_query_column(**query_params)

    response.update(table_info)
    query_params['user'] = user.id
    response['query_params'] = query_params
    if error:
        response['error'] = error


def column_sum_action(user, request_items, response):
    db = ri_get_str(request_items, 'db') or get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
        return response_with_message(response, "База данных не задана!", 'error')

    if not tables[0]:
        return response_with_message(response, "Таблица не задана!", 'error')

    column = ri_get_str(request_items, 'column')

    if not column:
        return response_with_message(response, "Колонка не задана!", 'error')

    search = ri_get_str(request_items, 'search')    # Строка для поиска
    filter_dict = ri_get_obj(request_items, 'filter_json')

    query_params = dict(
        user = user,
        db = db,
        tables = tables,
        column = column,
        search = search,
        filter = filter_dict,
    )

    table_info, error = qi_query_sum(**query_params)

    response.update(table_info)
    query_params['user'] = user.id
    response['query_params'] = query_params
    if error:
        response['error'] = error


def table_view_action(user, request_items, response):
    db = ri_get_str(request_items, 'db') or get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
        return response_with_message(response, "База данных не задана!", 'error')

    if not tables[0]:
        return response_with_message(response, "Таблица не задана!", 'error')

    offset = ri_get_int(request_items, 'offset')      # Требуемый первый ряд
    limit  = ri_get_int(request_items, 'limit', 100)  # Требуемое кол-во рядов
    search = ri_get_str(request_items, 'search')      # Строка для поиска
    search = ri_get_str(request_items, 'sSearch', search) # Строка для поиска

    columns_tuple = ri_get_tuple(request_items, 'columns')
    distinct_column = ri_get_str(request_items, 'distinct_column')

    # Если заданы короткие имена колонок - добавляем к ним название первой таблицы
    table = tables[0]
    columns = list(columns_tuple)
    for i in range(len(columns)):
        if '.' not in columns[i]:
            columns[i] = "{0}.{1}".format(table, columns[i])

    filter_dict  = ri_get_obj(request_items, 'filter_json')
    sorting_dict = ri_get_obj(request_items, 'sorting_json')

    query_params = dict(
        user = user,
        db = db,
        tables  = tables,
        search  = search,
        filter  = filter_dict,
        sorting = sorting_dict,
        offset  = offset,
        limit   = limit,
        columns = columns,
        distinct_column = distinct_column,
    )

    table_info, rows, error = qi_query(**query_params)

    response.update(table_info)
    query_params['user'] = user.id
    response['query_params'] = query_params

    if 'sEcho' in response:
        response['iTotalRecords']        = table_info['full_rows_count']
        response['iTotalDisplayRecords'] = table_info['filtered_rows_count']
        response['aaData'] = rows
    else:
        response['rows'] = rows

    if error:
        response['error'] = error


def column_district_action(user, request_items, response):
    db = ri_get_str(request_items, 'db') or get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
        return response_with_message(response, "База данных не задана!", 'error')

    if not tables[0]:
        return response_with_message(response, "Таблица не задана!", 'error')

    column = ri_get_str(request_items, 'column')

    if not column:
        return response_with_message(response, "Колонка не задана!", 'error')

    offset = ri_get_int(request_items, 'offset')      # Требуемый первый ряд
    limit  = ri_get_int(request_items, 'limit', 100)  # Требуемое кол-во рядов
    search = ri_get_str(request_items, 'search')      # Строка для поиска
    search = ri_get_str(request_items, 'sSearch', search) # Строка для поиска

    filter_dict  = ri_get_obj(request_items, 'filter_json')
    sorting_dict = ri_get_obj(request_items, 'sorting_json')

    query_params = dict(
        user = user,
        db = db,
        tables  = tables,
        search  = search,
        filter  = filter_dict,
        sorting = sorting_dict,
        offset  = offset,
        limit   = limit,
        distinct_column = column,
    )

    table_info, rows, error = qi_query(**query_params)

    response.update(table_info)
    query_params['user'] = user.id
    response['query_params'] = query_params

    if 'sEcho' in response:
        response['iTotalRecords']        = table_info['full_rows_count']
        response['iTotalDisplayRecords'] = table_info['filtered_rows_count']
        response['aaData'] = rows
    else:
        response['rows'] = [row[0] for row in rows]

    if error:
        response['error'] = error
