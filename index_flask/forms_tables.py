#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-21

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import time, math

from sqlalchemy import desc, not_
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
        '', '=', '!=', '=(int)', '!=(int)', '~', '!~', '>', '>=', '<', '<=',
        'consist', 'starts with', 'ends with',
        'in', 'not in', 'between', 'not between',
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
    plain = SelectField('Plain')


    def __init__(self, form, mtable=None, columns=None, templates_list=None, engine=None, **kargs):
        super(TableCondForm, self).__init__(form, **kargs)

        self.mtable = mtable
        self.engine = engine

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
        self.plain.choices = [['on', 'On'], ['off', 'Off']]


    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        return True


    def get_criterion(self):
        mcriterion = []
        criterion = []
        if self.column1.data and self.column1.data != 'None':
            mclause, clause = self.parse_clause(self.column1.data, [self.condition1.data, self.value1.data])
            if clause:
                mcriterion.append(mclause)
                criterion.append(clause)
        if self.column2.data and self.column2.data != 'None':
            mclause, clause = self.parse_clause(self.column2.data, [self.condition2.data, self.value2.data])
            if clause:
                mcriterion.append(mclause)
                criterion.append(clause)
        if self.column3.data and self.column3.data != 'None':
            mclause, clause = self.parse_clause(self.column3.data, [self.condition3.data, self.value3.data])
            if clause:
                mcriterion.append(mclause)
                criterion.append(clause)

        return mcriterion, criterion


    def get_order(self):
        morder = []
        order = []
        if self.sorting1.data and self.sorting1.data != 'None':
            mcolumn, sort_column = self.parse_order(self.sorting1.data, self.sort_dir1.data)
            if sort_column:
                morder.append(mcolumn)
                order.append(sort_column)
        if self.sorting2.data and self.sorting2.data != 'None':
            mcolumn, sort_column = self.parse_order(self.sorting2.data, self.sort_dir2.data)
            if sort_column:
                morder.append(mcolumn)
                order.append(sort_column)
        if self.sorting3.data and self.sorting3.data != 'None':
            mcolumn, sort_column = self.parse_order(self.sorting3.data, self.sort_dir3.data)
            if sort_column:
                morder.append(mcolumn)
                order.append(sort_column)

        return morder, order


    def parse_clause(self, column, value):
        mt = False
        if self.mtable is not None:
            mt = True
            mcolumn = get_column(self.mtable, column)
            if mcolumn is None:
                return

        clause = ''
        mclause = None

        if isinstance(value, list):
            condition, value = value
        else:
            condition = ''

        if not condition:
            if value is None:
                clause = "{0} is null".format(column)
                mclause = mcolumn == None if mt else clause
            elif isinstance(value, string_types):
                if value.isdigit():
                    value = int(value)
                    clause = "{0} = {1}".format(column, value)
                else:
                    clause = "{0} = '{1}'".format(column, value)
                mclause = mcolumn == value if mt else clause
            elif isinstance(value, int):
                clause = "{0} = {1}".format(column, value)
                mclause = mcolumn == value if mt else clause
            elif isinstance(value, float):
                clause = "{0} like '{1}'".format(column, value)
                mclause = mcolumn.like(value) if mt else clause

        else:
            if condition == '=' or condition == '==':
                if value.isdigit():
                    value = int(value)
                    clause = "{0} = {1}".format(column, value)
                else:
                    clause = "{0} = '{1}'".format(column, value)
                mclause = mcolumn == value if mt else clause
            elif condition == '!=':
                if value.isdigit():
                    value = int(value)
                    clause = "{0} != {1}".format(column, value)
                else:
                    clause = "{0} != '{1}'".format(column, value)
                mclause = mcolumn != value if mt else clause
            elif condition == '~':
                clause = "{0} like '{1}'".format(column, value)
                mclause = mcolumn.like(value) if mt else clause
            elif condition == '!~':
                clause = "{0} not like '{1}'".format(column, value)
                mclause = not_(mcolumn.like(value)) if mt else clause
            elif condition == '>':
                if value.isdigit():
                    value = int(value)
                    clause = "{0} > {1}".format(column, value)
                else:
                    clause = "{0} > '{1}'".format(column, value)
                mclause = mcolumn > value if mt else clause
            elif condition == '>=':
                if value.isdigit():
                    value = int(value)
                    clause = "{0} >= {1}".format(column, value)
                else:
                    clause = "{0} >= '{1}'".format(column, value)
                mclause = mcolumn >= value if mt else clause
            elif condition == '<':
                if value.isdigit():
                    value = int(value)
                    clause = "{0} < {1}".format(column, value)
                else:
                    clause = "{0} < '{1}'".format(column, value)
                mclause = mcolumn < value if mt else clause
            elif condition == '<=':
                if value.isdigit():
                    value = int(value)
                    clause = "{0} <= {1}".format(column, value)
                else:
                    clause = "{0} <= '{1}'".format(column, value)
                mclause = mcolumn <= value if mt else clause

            elif condition == 'consist':
                clause = "{0} like '%{1}%'".format(column, value)
                mclause = mcolumn.like("%{0}%".format(value)) if mt else clause
            elif condition == 'starts with':
                clause = "{0} like '{1}%'".format(column, value)
                mclause = mcolumn.like("{0}%".format(value)) if mt else clause
            elif condition == 'ends with':
                clause = "{0} like '%{1}'".format(column, value)
                mclause = mcolumn.like("%{0}".format(value)) if mt else clause

            elif condition == 'in':
                values = value.split(',')
                value = "','".join(values)
                clause = "{0} in ('{1}')".format(column, value)
                mclause = mcolumn.in_(*[values]) if mt else clause
            elif condition == 'not in':
                values = value.split(',')
                value = "','".join(values)
                clause = "{0} not in ('{1}')".format(column, value)
                mclause = not_(mcolumn.in_(*[values])) if mt else clause
            elif condition == 'between':
                value1, value2 = value.split(',')
                clause = "{0} between '{1}' and '{2}'".format(column, value1, value2)
                mclause = mcolumn.between(value1, value2) if mt else clause
            elif condition == 'not between':
                value1, value2 = value.split(',')
                clause = "{0} not between '{1}' and '{2}'".format(column, value1, value2)
                mclause = not_(mcolumn.between(value1, value2)) if mt else clause

            elif condition == 'is None':
                clause = "{0} is null".format(column)
                mclause = mcolumn == None if mt else clause
            elif condition == 'not is None':
                clause = "{0} is not null".format(column)
                mclause = mcolumn != None if mt else clause
            elif condition == 'is empty':
                clause = "{0} = ''".format(column)
                mclause = mcolumn == '' if mt else clause
            elif condition == 'not is empty':
                clause = "{0} != ''".format(column)
                mclause = mcolumn != '' if mt else clause

        if mt and self.engine:
            clause = str(mclause.compile(self.engine, compile_kwargs={"literal_binds": True}))

        return mclause, clause


    def parse_order(self, column, cond):
        sort_column = "{0} desc".format(column) if cond == 'DESC' else column

        if self.mtable is not None:
            column = get_column(self.mtable, column)
            if column is None:
                return

            mcolumn = desc(column) if cond == 'DESC' else column

        else:
            mcolumn = sort_column

        return mcolumn, sort_column
