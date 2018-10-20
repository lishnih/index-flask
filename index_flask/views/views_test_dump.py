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

    obj = [1, 2, 3, None, '<i>table</i>', True, False]

    return render_template('dump_list.html',
             obj = obj,
           )


@app.route('/test_dump/dict')
def test_dump_dict():
    if not debug_permission.can():
        abort(404)

    obj = dict(a = 1, b = 2, c = 3, none = None, table = '<i>table</i>', t = True, f = False)

    return render_template('dump_dict.html',
             obj = obj,
           )


@app.route('/test_dump/json')
def test_dump_json():
    if not debug_permission.can():
        abort(404)

    rows = [
      None,
      dict(a = 1, b = 2, c = 3, none = None, table = '<i>table</i>', t = True, f = False),
      dict(a = 21, b = 22, c = 23, none = None),
      1,
    ]

    return render_template('dump_json.html',
             rows = rows,
           )


@app.route('/test_dump/table')
def test_dump_table():
    if not debug_permission.can():
        abort(404)

    names = ['a', 'b', 'c', 'none', '<i>table</i>', 't', 'f']
    rows = [
      [1, 2, 3, None, '<i>table1</i>', True, False],
      [1, 2, 3, None, '<i>table2</i>', True, False],
      [1, 2, 3, None, '<i>table3</i>', True, False],
    ]

    return render_template('dump_table.html',
             names = names,
             rows = rows,
           )


@app.route('/test_dump/table_unsafe')
def test_dump_table_unsafe():
    if not debug_permission.can():
        abort(404)

    names = ['a', 'b', 'c', 'none', '<i>table</i>', 't', 'f']
    rows = [
      [1, 2, 3, None, '<i>table1</i>', True, False],
      [1, 2, 3, None, '<i>table2</i>', True, False],
      [1, 2, 3, None, '<i>table3</i>', True, False],
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
              ['a', 'b', 'c', 'none', '<i>table</i>', 't', 'f'],
              [
                [1, 2, 3, None, '<i>table1</i>', True, False],
                [1, 2, 3, None, '<i>table2</i>', True, False],
                [1, 2, 3, None, '<i>table3</i>', True, False],
              ],
              '<b><i>Table 1</i></b>',
            ],
            [
              ['a', 'b', 'c', 'none'],
              [
                [21, 22, 23, None],
                [31, 32, 33, None],
                [41, 42, 43, None],
              ],
              '<b><i>Table 2</i></b>',
            ]
          ]

    return render_template('dump_tables.html',
             obj = obj,
           )
