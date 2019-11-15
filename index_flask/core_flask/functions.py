#!/usr/bin/env python
# coding=utf-8
# Stan 2018-08-02

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, url_for


def get_next(default='index', back=False):
    base = url_for('index')
    next = request.args.get('next', '')
    if not next.startswith(base):
        next = ''

    return next or \
           request.referrer if back else False or \
           url_for(default)


def debug_query(query):
    try:
        return str(query)
    except Exception as e:
        return repr(query)
