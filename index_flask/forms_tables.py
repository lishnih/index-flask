#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-21

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import time, math

from sqlalchemy import desc, distinct, func, and_, or_, not_
from wtforms import Form, StringField, IntegerField, SelectField, validators

from .core.backwardcompat import *
from .core.db import get_columns_names, get_column


class TableCondForm(Form):
    offset = IntegerField('Offset')
    limit = IntegerField('Limit')

    column1 = SelectField('Filter')
    column2 = SelectField('Filter')
    column3 = SelectField('Filter')

    conditions = [[i, i] for i in [
        '', '=', '!=', '~', '!~', '>', '>=', '<', '<=',
        'consist', 'in', 'not in', 'between', 'not between',
        'is None', 'not is None', 'is empty', 'not is empty',
    ]]
    condition1 = SelectField('Filter', choices=conditions)
    condition2 = SelectField('Filter', choices=conditions)
    condition3 = SelectField('Filter', choices=conditions)

    value1 = StringField('Filter')
    value2 = StringField('Filter')
    value3 = StringField('Filter')

    sorting1 = SelectField('Sorting')
    sorting2 = SelectField('Sorting')
    sorting3 = SelectField('Sorting')

    sort_dirs = [[i, i] for i in ['ASC', 'DESC']]
    sort_dir1 = SelectField('Filter', choices=sort_dirs)
    sort_dir2 = SelectField('Filter', choices=sort_dirs)
    sort_dir3 = SelectField('Filter', choices=sort_dirs)

    template = SelectField('Template')
    unlim = SelectField('Unlimited')


    def __init__(self, form, mtable=None, columns=None, templates_list=None, **kwargs):
        super(TableCondForm, self).__init__(form, **kwargs)

        self.mtable = mtable

        if not columns:
            columns = [i for i in get_columns_names(mtable)]

        fields = [[i, i] for i in columns]
        fields.insert(0, ['', ''])

        self.column1.choices = fields
        self.column2.choices = fields
        self.column3.choices = fields

        self.sorting1.choices = fields
        self.sorting2.choices = fields
        self.sorting3.choices = fields

        if not templates_list:
            templates_list = []

        fields = [[i, i] for i in templates_list]
        fields.insert(0, ['', ''])

        self.template.choices = fields

        self.unlim.choices = [['off', 'Off'], ['on', 'On']]


    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        return True


    def get_criterion(self):
        criterion = []
        if self.column1.data and self.column1.data <> 'None':
            clause = self.parse_clause(self.column1.data, [self.condition1.data, self.value1.data])
            if clause is not None:
                criterion.append(clause)
        if self.column2.data and self.column2.data <> 'None':
            clause = self.parse_clause(self.column2.data, [self.condition2.data, self.value2.data])
            if clause is not None:
                criterion.append(clause)
        if self.column3.data and self.column3.data <> 'None':
            clause = self.parse_clause(self.column3.data, [self.condition3.data, self.value3.data])
            if clause is not None:
                criterion.append(clause)

        return criterion


    def get_order(self):
        order = []
        if self.sorting1.data and self.sorting1.data <> 'None':
            sort_column = self.parse_order(self.sorting1.data, self.sort_dir1.data)
            if sort_column is not None:
                order.append(sort_column)
        if self.sorting2.data and self.sorting2.data <> 'None':
            sort_column = self.parse_order(self.sorting2.data, self.sort_dir2.data)
            if sort_column is not None:
                order.append(sort_column)
        if self.sorting3.data and self.sorting3.data <> 'None':
            sort_column = self.parse_order(self.sorting3.data, self.sort_dir3.data)
            if sort_column is not None:
                order.append(sort_column)

        return order


    def parse_clause(self, column, value):
        mt = self.mtable is not None

        if mt:
            column = get_column(self.mtable, column)
            if column is None:
                return

        clause = None
        if value is None:
            clause = column == None if mt else \
                     "{0} is null".format(column)
        elif isinstance(value, basestring) or isinstance(value, int):
            clause = column == value if mt else \
                     "{0}='{1}'".format(column, value)
        elif isinstance(value, float):
            clause = column.like(value) if mt else \
                     "{0} like '{1}'".format(column, value)
        else:
            condition, value = value
            if not condition and value:
                clause = column == value if mt else \
                         "{0}='{1}'".format(column, value)
            if condition == '=' or condition == '==':
                clause = column == value if mt else \
                         "{0}='{1}'".format(column, value)
            elif condition == '!=':
                clause = column != value if mt else \
                         "{0}!='{1}'".format(column, value)
            elif condition == '~':
                clause = column.like(value) if mt else \
                         "{0} like '{1}'".format(column, value)
            elif condition == '!~':
                clause = not_(column.like(value)) if mt else \
                         "{0} not like '{1}'".format(column, value)
            elif condition == '>':
                clause = column > value if mt else \
                         "{0}>'{1}'".format(column, value)
            elif condition == '>=':
                clause = column >= value if mt else \
                         "{0}>='{1}'".format(column, value)
            elif condition == '<':
                clause = column < value if mt else \
                         "{0}<'{1}'".format(column, value)
            elif condition == '<=':
                clause = column <= value if mt else \
                         "{0}<='{1}'".format(column, value)
            elif condition == 'consist':
                clause = column.like("%{0}%".format(value)) if mt else \
                         "{0} like '%{1}%'".format(column, value)

        return clause


    def parse_order(self, column, cond):
        if self.mtable is not None:
            column = get_column(self.mtable, column)
            if column is None:
                return

            return desc(column) if cond == 'DESC' else column

        else:
            return "{0} desc".format(column) if cond == 'DESC' else column
