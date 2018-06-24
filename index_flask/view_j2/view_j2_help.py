#!/usr/bin/env python
# coding=utf-8
# Stan 2012-02-29

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from .request_interface import *
from .response_interface import *


def actions_list_action(request_items, response):
    response['rows'] = [
        'actions_list',
        'action_params_list',
        'default_db',
        'set_default_db',
        'dbs_list',
        'tables_list',
        'columns_list',
        'table_count',
        'table_view',
        'column_func',
        'column_sum',
        'column_district',
        'search',
        'query',
        'favorite_page_add',
    ]


def action_params_list_action(request_items, response):
    req_action = ri_get_str(request_items, 'req_action')

    if not req_action:
        return response_with_message(response, "Команда не задана!", 'error')

    elif req_action == 'actions_list':
        response['description'] = "Перечень команд"
        response['rows'] = []

    elif req_action == 'action_params_list':
        response['description'] = "Перечень параметров команды"
        response['rows'] = ['req_action']

    elif req_action == 'default_db':
        response['description'] = "Получить БД по умолчанию"
        response['rows'] = []

    elif req_action == 'set_default_db':
        response['description'] = "Установить БД по умолчанию"
        response['rows'] = ['db']

    elif req_action == 'dbs_list':
        response['description'] = "Список доступных БД"
        response['rows'] = []

    elif req_action == 'tables_list':
        response['description'] = "Список доступных таблиц"
        response['rows'] = ['db']

    elif req_action == 'columns_list':
        response['description'] = "Список колонок в таблице/таблицах"
        response['rows'] = ['db', 'table', 'tables', 'fullnames']

    elif req_action == 'table_count':
        response['description'] = "Количество рядов в таблице/нескольких таблицах (связанных между собой)"
        response['rows'] = ['db', 'table', 'tables', 'search', 'filter_json']

    elif req_action == 'table_view':
        response['description'] = "Вывод таблицы/нескольких таблиц (связанных между собой)"
        response['rows'] = ['db', 'table', 'tables', 'search', 'offset', 'limit', 'columns', 'filter_json', 'sorting_json']

    elif req_action == 'column_func':
        response['description'] = "Производит заданное действие над полем в таблице/нескольких таблицах (связанных между собой)"
        response['rows'] = ['db', 'table', 'tables', 'column', 'func', 'search', 'filter_json']

    elif req_action == 'column_sum':
        response['description'] = "Сумма значений поля в таблице/нескольких таблицах (связанных между собой)"
        response['rows'] = ['db', 'table', 'tables', 'column', 'search', 'filter_json']

    elif req_action == 'column_district':
        response['description'] = "Вывод значений заданной колонки таблицы"
        response['rows'] = ['db', 'table', 'tables', 'column', 'search', 'offset', 'limit', 'filter_json', 'sorting_json']

    elif req_action == 'search':
        response['description'] = "Поиск во всех таблицах"
        response['rows'] = ['search']

    elif req_action == 'query':
        response['description'] = "Выполнение запроса"
        response['rows'] = ['db', 'query']

    elif req_action == 'favorite_page_add':
        response['description'] = "Добавление страницы в избранное"
        response['rows'] = ['title', 'url']

    else:
        return response_with_message(response, "Неизвестная команда!", 'error')
