#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-17

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os


def parse_input(sid, checked, action, **kargs):
    kargs['action'] = action
    data = ''
    for key, val in kargs.items():
        data += ' data-{0}="{1}"'.format(key, val)
    cls = 'for_action'
    cls = ' class="{0}"'.format(cls) if cls else ''
    sid = ' id="{0}"'.format(sid) if sid else ''

    return '<input type="checkbox"{0}{1}{2}{3} />'.format(cls, sid, data,
           'checked' if checked else '')


def parse_span(sid, text, action, **kargs):
    kargs['action'] = action
    data = ''
    for key, val in kargs.items():
        data += ' data-{0}="{1}"'.format(key, val)
    cls = 'a for_action'
    cls = ' class="{0}"'.format(cls) if cls else ''
    sid = ' id="{0}"'.format(sid) if sid else ''

    return '<span{0}{1}{2}>{3}</span>'.format(cls, sid, data, text)
