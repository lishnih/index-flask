#!/usr/bin/env python
# coding=utf-8
# Stan 2012-02-06

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from .request_interface import *
from .response_interface import *
from .query_interface import *

from ..models import db, Register, Favorite


def set_default_db_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = ri_get_str(request_items, 'db')
    db = user_db.set_default_db(user, db)

    response['rows'] = [db]


def default_db_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = user_db.get_default_db(user)

    response['rows'] = [db]


def dbs_list_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    response['rows'] = [i for i in user_db.get_dbs_list(user)]


def tables_list_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = ri_get_str(request_items, 'db') or user_db.get_default_db(user)

    if not db:
#       return response_with_message(response, "База данных не задана!", 'error')
        return response_redirect(response, '/user_db_set_default_db/')

    response['rows'] = user_db.get_metadata(user, db).tables.keys()


def columns_list_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = ri_get_str(request_items, 'db') or user_db.get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
#         return response_with_message(response, "База данных не задана!", 'error')
        return response_redirect(response)

    if not tables[0]:
        return response_with_message(response, "Таблица не задана!", 'error')

    fullnames = ri_get_int(request_items, 'fullnames')

    columns_list = qi_columns_list(user, db, tables, fullnames)

    response['rows'] = columns_list


def table_count_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = ri_get_str(request_items, 'db') or user_db.get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
#         return response_with_message(response, "База данных не задана!", 'error')
        return response_redirect(response)

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


def table_view_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = ri_get_str(request_items, 'db') or user_db.get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
#         return response_with_message(response, "База данных не задана!", 'error')
        return response_redirect(response)

    if not tables[0]:
        return response_with_message(response, "Таблица не задана!", 'error')

    offset = ri_get_int(request_items, 'offset')      # Требуемый первый ряд
    limit  = ri_get_int(request_items, 'limit', 100)  # Требуемое кол-во рядов
    search = ri_get_str(request_items, 'search')      # Строка для поиска
    search = ri_get_str(request_items, 'sSearch', search) # Строка для поиска
    plain  = ri_get_int(request_items, 'plain', 1)    # Тип возвращаемых данных (записей)

    columns_tuple = ri_get_tuple(request_items, 'columns')
    distinct_columns = ri_get_str(request_items, 'distinct_column')
    distinct_columns = ri_get_str(request_items, 'distinct_columns')

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
        distinct_columns = distinct_columns,
        plain = plain,
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


def column_func_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = ri_get_str(request_items, 'db') or user_db.get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
#         return response_with_message(response, "База данных не задана!", 'error')
        return response_redirect(response)

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
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = ri_get_str(request_items, 'db') or user_db.get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
#         return response_with_message(response, "База данных не задана!", 'error')
        return response_redirect(response)

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


def column_district_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = ri_get_str(request_items, 'db') or user_db.get_default_db(user)
    tables = ri_get_str(request_items, 'table'),
    tables = ri_get_tuple(request_items, 'tables', tables)

    if not db:
#         return response_with_message(response, "База данных не задана!", 'error')
        return response_redirect(response)

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
        distinct_columns = column,
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


def collect_columns(mtable, root=None):
    if root is None:
        root = mtable
    mcolumns = []
    mcolumns2 = []
    foreign_key = False
    for c in mtable.columns:
        if c.foreign_keys and not foreign_key:
            foreign_key = True
            first, = c.foreign_keys
            root = root.join(first.column.table, first.parent==first.column)
            mcolumns2, root = collect_columns(first.column.table, root)
        elif c.name != 'id':
            mcolumns.append(c)

    if mcolumns2:
        mcolumns = mcolumns2 + mcolumns

    return mcolumns, root


def search_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    search = ri_get_str(request_items, 'search')
    dbs_list = user_db.get_dbs_list(user)

    rows = []
    drows = {}
    for db in dbs_list:
        drow = {}
        db_uri, session, metadata = user_db.get_db(user, db)
        for mtable in metadata.sorted_tables:
            tablename = unicode(mtable.name)

            record = Register.query.filter_by(
              _user_id = user.id,
              section = 'search_sql_query',
              dir = '*',                      # !!!
              name = tablename,
            ).first()
            if record:
                sql = record.value.format(tablename, search)
                res = session.execute(sql)
                names = res.keys()
                rows1 = [[j for j in i] for i in res.fetchall()]
                if rows1:
                    drow[tablename] = {
                        'names': names,
                        'rows': rows1,
                        'query': sql,
                    }
            else:
                mcolumns, mtable = collect_columns(mtable)
                or_st = []
                for c in mcolumns:
                    or_st.append(c.like("%{0}%".format(search)))

                s = select(mcolumns).select_from(mtable).where(or_(*or_st))
                res = session.execute(s)
                names = res.keys()
                rows1 = [[j for j in i] for i in res.fetchall()]
                if rows1:
                    drow[tablename] = {
                        'names': names,
                        'rows': rows1,
                        'query': str(s),
                    }

        if drow:
            rows.append(db)
            drow['__tables__'] = drow.keys()
            drows[db] = drow


    response['rows'] = rows
    response['drows'] = drows


def query_action(user, request_items, response):
    user_db = require_ext('user_db')
    if not user_db:
        return response_with_message(response, "Не загружен модуль 'user_db'!", 'error')

    db = ri_get_str(request_items, 'db') or user_db.get_default_db(user)
    query = ri_get_str(request_items, 'query')

    if not db:
        return response_with_message(response, "База данных не задана!", 'error')

    db_uri, session, metadata = user_db.get_db(user, db)
    res = session.execute(query)

    response['names'] = res.keys()
    response['rows'] = [[j for j in i] for i in res.fetchall()]


def favorite_page_add_action(user, request_items, response):
    title = ri_get_str(request_items, 'title')
    url = ri_get_str(request_items, 'url')

    favorite = Favorite.query.filter_by(title=title, url=url, _user_id=user.id).first()
    if favorite:
        response['message'] = "Уже добавлено ранее!"

    else:
        favorite = Favorite(
            title = title,
            url = url,
            user = user,
        )
        db.session.add(favorite)
        db.session.commit()

        response['message'] = "Успешно добавлено!"


def get_favorites_action(user, request_items, response):
    favorites = Favorite.query.filter_by(_user_id=user.id).all()
    rows = []
    for f in favorites:
        rows.append({a: b for a, b in f.__dict__.items() if a[0] !="_"})
    response['rows'] = rows
