#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
import os

from flask import (g, request, config, render_template, url_for, session,
                   abort)

from flask_login import current_user
from flask_principal import Permission, RoleNeed

from ..app import app
from ..core.dump_html import html


# ===== Roles =====

debug_permission = Permission(RoleNeed('debug'))
# debug_permission = Permission()


# ===== Routes =====

@app.route('/debug/')
def debug():
    if not debug_permission.can():
        abort(404)

    output = []
    for rule in app.url_map.iter_rules():
        options, options_str = {}, {}
        for seq, arg in enumerate(rule.arguments, 1):
            options[arg] = seq
            options_str[arg] = "<{0}>".format(arg)

        url = url_for(rule.endpoint, **options)
        args = rule.arguments if rule.arguments else ''
        methods = ','.join(rule.methods)
        f = app.view_functions.get(rule.endpoint)
#       loc = f.__code__.co_filename if f else ''   # f.func_code.co_filename
        m = sys.modules.get(f.__module__)
        loc = m.__file__ if m else ''
        dirname = os.path.basename(os.path.dirname(loc))
        basename = os.path.basename(loc)
        loc = os.path.join(dirname, basename)
        output.append([url, args, methods, rule.endpoint, loc])

    return render_template('views/views_debug.html',
        title = 'Url mapping',
        without_sidebar = True,
        urls = sorted(output, key=lambda url: (url[4], url[0])),
        total = len(output),
    )


@app.route('/debug/current_user')
def debug_current_user():
    if not debug_permission.can():
        abort(404)

    return render_template('base.html',
        without_sidebar = True,
        html = html(current_user),
    )


@app.route('/debug/config')
def debug_config():
    if not debug_permission.can():
        abort(404)

    return render_template('base.html',
        without_sidebar = True,
        html = html(config),
    )


@app.route('/debug/request')
def debug_request():
    if not debug_permission.can():
        abort(404)

    return render_template('base.html',
        without_sidebar = True,
        html = html(request),
    )


@app.route('/debug/session')
def debug_session():
    if not debug_permission.can():
        abort(404)

    l = []
    if session:
        for key, val in session.items():
            l.append((key, val))

    return render_template('base.html',
        without_sidebar = True,
        html = html(session),
        names = ["Key", "Value"],
        rows = l,
    )


@app.route('/debug/g')
def debug_g():
    if not debug_permission.can():
        abort(404)

    return render_template('base.html',
        without_sidebar = True,
        html = html(g),
    )


@app.route('/debug/cookies')
def debug_cookies():
    if not debug_permission.can():
        abort(404)

    return render_template('base.html',
        without_sidebar = True,
        html = html(request.cookies),
    )
