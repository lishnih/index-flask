#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-10

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import render_template, flash

from flask_login import login_required

from ..app import app


# ===== Variables =====

test_d = dict(
    content_head = '<b>content_head</b>',
    content_head_muted = '<b>content_head_muted</b>',
    card_head = '<b>card_head</b>',
    card_rows = [
        '<b>card row 1</b>',
        '<b>card row 2</b>',
        '<b>card row 3</b>',
    ],
    html = '<b>html</b>',
    text = '<b>text</b>',
    sticky_footer = '<b>sticky_footer</b>',

    total = '<b>total</b>',
    shown = '<b>shown</b>',
    filtered = '<b>filtered</b>',
    names = ['<b>name_1</b>', '<b>name_2</b>', '<b>name_3</b>'],
    rows = [
        ['<b>cell_11</b>', '<b>cell_12</b>', '<b>cell_13</b>'],
        ['<b>cell_21</b>', '<b>cell_22</b>', '<b>cell_23</b>'],
    ],

    tables_wdest = [
        [
            ['<b>name_1</b>', '<b>name_2</b>', '<b>name_3</b>'],
            [
                ['<b>cell_11</b>', '<b>cell_12</b>', '<b>cell_13</b>'],
                ['<b>cell_21</b>', '<b>cell_22</b>', '<b>cell_23</b>'],
            ],
            'description 1 (unsafe)',
            'postscript 1 (unsafe)',
        ],
        [
            ['<b>name_1</b>', '<b>name_2</b>', '<b>name_3</b>'],
            [
                ['<b>cell_11</b>', '<b>cell_12</b>', '<b>cell_13</b>'],
                ['<b>cell_21</b>', '<b>cell_22</b>', '<b>cell_23</b>'],
            ],
            'description 2 (unsafe)',
            'postscript 2 (unsafe)',
        ],
    ],
)


# ===== Routes =====

@app.route("/test_base")
@login_required
def test_base():
    flash("Info flash message", 'info')
    flash("Warning flash message", 'warning')
    flash("Error flash message", 'error')

    return render_template('base.html',
        title = '<b>title</b>',
        **test_d
    )


@app.route("/test_injected")
@login_required
def test_injected():
    return render_template('p/test_injected.html')


@app.route("/test_layout2")
@login_required
def test_layout2():
    return render_template('p/test_layout2.html',
        title = '<b>title</b>',
        **test_d
    )
