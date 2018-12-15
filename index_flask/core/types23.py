#!/usr/bin/env python
# coding=utf-8
# Stan 2013-04-22


import sys


if sys.version_info >= (3,):
    class aStr():
        def __str__(self):
            return self.__unicode__()

    def cmp(a, b):
        return (a > b) - (a < b)

#   range = range

    def b(s):
        return s.encode('utf-8')

    def u(s):
        return s.decode('utf-8')

#   bytes = bytes
    unicode = str
#   str = str

    string_types = str,
    numeric_types = int, float, complex
    simple_types = int, float, complex, str, bytearray
    collections_types = list, tuple, set, frozenset
    all_types = (int, float, complex, str, bytearray,
                 list, tuple, set, frozenset, dict)

else:
    class aStr():
        def __str__(self):
            return self.__unicode__().encode('utf-8')

#   cmp = cmp

    range = xrange

    def b(s):
        return s

    def u(s):
        return s

    bytes = str
#   unicode = unicode
#   str = str

    string_types = basestring,
    numeric_types = int, long, float, complex
    simple_types = int, long, float, complex, basestring, bytearray
    collections_types = list, tuple, set, frozenset
    all_types = (int, long, float, complex, basestring, bytearray,
                 list, tuple, set, frozenset, dict)
