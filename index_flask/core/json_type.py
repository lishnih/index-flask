#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-27

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json
import logging

from sqlalchemy.types import TypeDecorator, Text


class JsonType(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        try:
            d = json.loads(value)

        except:
            d = {}
            logging.error("JsonType converting error: '{0}'".format(value))

        return d
