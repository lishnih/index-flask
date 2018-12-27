#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-11

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, render_template, jsonify, flash, escape
from jinja2 import Markup, escape
from werkzeug.wrappers import Response

from flask_principal import Permission, RoleNeed

from ..core.types23 import *


debug_permission = Permission(RoleNeed('debug'))


def render_ext(template_name_or_list=None, default=None, message="",
        format=None, form=None, **context):
    format = format or request.values.get('format')

    if not debug_permission.can():
        context.pop('debug', '')

    result = "success"
    if isinstance(message, tuple):
        message, result = message

    if format == 'json':
#       context = {k: v for k, v in context.items() if k in \
#           ['action', 'rows', 'debug']}
        return jsonify(dict(
            result = result,
            message = message,
            **context
        ))

    if message:
        flash(message, result or "success")

    if isinstance(default, Response) and not format:
        return default

    return "No template defined!" if not template_name_or_list else \
        render_template(template_name_or_list,
            modal = format == 'modal',
            form = form,
            **context
        )


def swap(s, limit=0):
    if isinstance(s, string_types):
        s = escape(s)   # не требуется при render_template
        if limit and len(s) > limit:
            s = Markup("""<span class="truncated">{0}</span>
<span class="hidden_text" title="{1}">[...]</span>""".format(s[0:limit-20], s))

    return s


def render_format(template_name, **context):
    format = request.values.get('format')

    if not debug_permission.can():
        context.pop('debug')

    truncate = context.pop('truncate', None)
    flash_t = context.pop('flash_t', None)

    if format == 'json':
        for key, val in context.items():
            if not isinstance(val, all_types):
                context.pop(key)

        if flash_t:
            message, result = flash_t if len(flash_t) > 1 else flash_t, 'prompt'
            context['flash_cat'] = result
            context['flash_message'] = message

        if 'rows' in context:
            context['rows'] = [[escape(i) for i in row] for row in context['rows']]
            context['rows'] = [[swap(i, truncate) for i in row] for row in context['rows']]

        return jsonify(**context)

    else:
        if flash_t:
            flash(*flash_t)

        if 'rows' in context:
            context['rows'] = [[swap(i, truncate) for i in row] for row in context['rows']]

        return render_template(template_name, **context)
