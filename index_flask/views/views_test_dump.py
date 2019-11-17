#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-15

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, render_template, abort

from flask_principal import Permission, RoleNeed

from ..app import app


# ===== Roles =====

debug_permission = Permission(RoleNeed('debug'))
# debug_permission = Permission()


# ===== Routes =====

@app.route('/test_dump/')
def test_dump():
    if not debug_permission.can():
        abort(404)

    tests_list = ['list', 'dict', 'json', 'table', 'table_unsafe', 'tables']

    return render_template('dump_list.html',
        obj_a = tests_list,
    )


@app.route('/test_dump/list')
def test_dump_list():
    if not debug_permission.can():
        abort(404)

    obj = [0, 1, 2.3, -100, 'text', None, '<i>inclined</i>', True, False]

    return render_template('dump_list.html',
        obj = obj,
    )


@app.route('/test_dump/dict')
def test_dump_dict():
    if not debug_permission.can():
        abort(404)

    obj = dict(a = 0, b = 1, c = 2.3, d = -100, text = 'text', none = None, inclined = '<i>inclined</i>', true = True, false = False)

    return render_template('dump_dict.html',
        obj = obj,
    )


@app.route('/test_dump/json')
def test_dump_json():
    if not debug_permission.can():
        abort(404)

    rows = [
        None,
        dict(a = 0, b = 11, c = 2.3, d = -100, text = 'text 1', none = None, inclined = '<i>inclined 1</i>', true = True, false = False),
        dict(a = 0, b = 21, c = 2.3, d = -100, text = 'text 2', none = None, inclined = '<i>inclined 2</i>', true = True, false = False),
        1,
    ]

    return render_template('dump_json.html',
        rows = rows,
    )


@app.route('/test_dump/table')
def test_dump_table():
    if not debug_permission.can():
        abort(404)

    names = ['a', 'b', 'c', 'd', 'text', 'none', '<i>inclined</i>', 'true', 'false']
    rows = [
        [0, 11, 2.3, -100, 'text 1', None, '<i>inclined 1</i>', True, False],
        [0, 21, 2.3, -100, 'text 2', None, '<i>inclined 2</i>', True, False],
        [0, 31, 2.3, -100, 'text 3', None, '<i>inclined 3</i>', True, False],
    ]

    return render_template('dump_table.html',
        names = names,
        rows = rows,
    )


@app.route('/test_dump/table_unsafe')
def test_dump_table_unsafe():
    if not debug_permission.can():
        abort(404)

    names = ['a', 'b', 'c', 'd', 'text', 'none', '<i>inclined</i>', 'true', 'false']
    rows = [
        [0, 11, 2.3, -100, 'text 1', None, '<i>inclined 1</i>', True, False],
        [0, 21, 2.3, -100, 'text 2', None, '<i>inclined 2</i>', True, False],
        [0, 31, 2.3, -100, 'text 3', None, '<i>inclined 3</i>', True, False],
    ]

    return render_template('dump_table_unsafe.html',
        names = names,
        rows = rows,
    )


@app.route('/test_dump/tables')
def test_dump_tables():
    if not debug_permission.can():
        abort(404)

    obj = [
            [
              ['a', 'b', 'c', 'd', 'text', 'none', '<i>inclined</i>', 'true', 'false'],
              [
                [0, 11, 2.3, -100, 'text 1', None, '<i>inclined 1</i>', True, False],
                [0, 21, 2.3, -100, 'text 2', None, '<i>inclined 2</i>', True, False],
                [0, 31, 2.3, -100, 'text 3', None, '<i>inclined 3</i>', True, False],
              ],
              '<b><i>bold inclined 1</i></b>',
            ],
            [
              ['a', 'b', 'c', 'none'],
              [
                [21, 22, 23.1, None],
                [31, 32, 33.2, None],
                [41, 42, 43.3, None],
              ],
              '<b><i>bold inclined 2</i></b>',
            ]
          ]

    return render_template('dump_tables.html',
        obj = obj,
    )
