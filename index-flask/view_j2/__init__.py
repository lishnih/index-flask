#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-11, 2016-06-05

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from .view_j2_help import *
from .view_j2_funcs import *


def view_j2(request):
    response = prepare_response(request)

    action, request_items = get_action(request, response)
    if not action:
        return response_with_message(response, "Нет запроса!", 'warning')

    logged_in = 'noname'

# view_j2_help

    if   action == 'actions_list':
        actions_list_action(request_items, response)

    elif action == 'action_params_list':
        action_params_list_action(request_items, response)


# view_j2_funcs

    elif action == 'tables_list':
        tables_list_action(logged_in, request_items, response)

    elif action == 'columns_list':
        columns_list_action(logged_in, request_items, response)

    elif action == 'table_count':
        table_count_action(logged_in, request_items, response)

    elif action == 'table_view':
        table_view_action(logged_in, request_items, response)

    elif action == 'column_func':
        column_func_action(logged_in, request_items, response)

    elif action == 'column_sum':
        column_sum_action(logged_in, request_items, response)

    elif action == 'column_district':
        column_district_action(logged_in, request_items, response)


    else:
        return response_with_message(response, "Запрос не опознан!", 'exception')

    return response
