#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-28

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask_login import current_user

from flask_sqlalchemy import BaseQuery
from sqlalchemy.sql import or_
from sqlalchemy.sql.selectable import _interpret_as_from


def filter_active(self):
    return self.filter_by(deleted=False)

BaseQuery.filter_active = filter_active


def filter_user(self, public=False):
    if public:
        # left reference stolen from sqlalchemy/orm/query.py#L2187
        left = self._entities[0].entity_zero_or_selectable
        left_tbl = _interpret_as_from(left)
        return self.filter(or_(left_tbl.c._user_id==current_user.id, left_tbl.c._user_id==None), left_tbl.c.deleted==False)
    else:
        return self.filter_by(_user_id=current_user.id, deleted=False)

BaseQuery.filter_user = filter_user
