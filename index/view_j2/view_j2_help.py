#!/usr/bin/env python
# coding=utf-8
# Stan 2012-02-29

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from .request_interface import *
from .response_interface import *


def actions_list_action(request_items, response):
    response['rows'] = [
        'actions_list',
        'action_params_list',
        'tables_list',
        'columns_list',
        'table_count',
        'table_view',
        'column_sum',
        'column_district',
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

    elif req_action == 'tables_list':
        response['description'] = "Список доступных таблиц"
        response['rows'] = []

    elif req_action == 'columns_list':
        response['description'] = "Список колонок в таблице/таблицах"
        response['rows'] = ['table', 'tables', 'fullnames']

    elif req_action == 'table_count':
        response['description'] = "Количество рядов в таблице/нескольких таблицах (связанных между собой)"
        response['rows'] = ['table', 'tables', 'search', 'filter_json']

    elif req_action == 'table_view':
        response['description'] = "Вывод таблицы/нескольких таблиц (связанных между собой)"
        response['rows'] = ['table', 'tables', 'search', 'offset', 'limit', 'columns', 'filter_json', 'sorting_json']

    elif req_action == 'column_sum':
        response['description'] = "Сумма значений поля в таблице/нескольких таблицах (связанных между собой)"
        response['rows'] = ['table', 'tables', 'column', 'search', 'filter_json']

    elif req_action == 'column_district':
        response['description'] = "Вывод значений заданной колонки таблицы"
        response['rows'] = ['table', 'tables', 'column', 'search', 'offset', 'limit', 'filter_json', 'sorting_json']

    else:
        return response_with_message(response, "Неизвестная команда!", 'error')
