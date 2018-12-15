#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-17

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)


def parse_input(sid, checked, action, cls = 'for_action', **kargs):
    kargs['action'] = action
    data = ['data-{0}="{1}"'.format(key, val) for key, val in kargs.items()]
    data = ' '.join(data)
    cls = ' class="{0}"'.format(cls) if cls else ''
    sid = ' id="{0}"'.format(sid) if sid else ''

    return '<input type="checkbox"{0}{1}{2}{3} />'.format(cls, sid, data,
           'checked' if checked else '')


def parse_span(sid, text, action, cls = 'a for_action', **kargs):
    kargs['action'] = action
    data = ['data-{0}="{1}"'.format(key, val) for key, val in kargs.items()]
    data = ' '.join(data)
    cls = ' class="{0}"'.format(cls) if cls else ''
    sid = ' id="{0}"'.format(sid) if sid else ''

    return '<span{0}{1}{2}>{3}</span>'.format(cls, sid, data, text)


def highlighted(text, color='info', bg='', b=True):
    text = '<b>{0}</b>'.format(text) if b else text
    return '<span class="{0}{1}">{2}</span>'.format(
        " text-{}".format(color) if color else '',
        " bg-{}".format(bg) if bg else '',
        text
    )
