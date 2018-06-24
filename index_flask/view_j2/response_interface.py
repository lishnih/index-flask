#!/usr/bin/env python
# coding=utf-8
# Stan 2012-02-06

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

# from ..core.dump_html import html


def prepare_response(request):
    response = dict(
        version = 2.1,
        _method = request.method,
        _get  = repr(request.args),
        _post = repr(request.form),
#       html = html(request),
    )

    response['rows']   = []
    response['aaData'] = []

    return response


def response_with_message(response, msg, msg_type='info'):
    if not response['rows']:
        response['rows'].append(msg)
    if not response['aaData']:
        response['iTotalRecords']        = 1
        response['iTotalDisplayRecords'] = 1
        response['aaData'] = [['' for i in range(10)]]
        response['aaData'][0][0] = msg
    if msg_type:
        response[msg_type] = msg

    return response


def response_redirect(response, url=None):
    response['action'] = 'redirect'
    response['url'] = url

    return response
