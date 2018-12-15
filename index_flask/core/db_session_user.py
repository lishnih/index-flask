#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-08

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import re
from contextlib import contextmanager

from flask_login import login_required, current_user

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy_utils.functions import database_exists


dbname_ptrn = re.compile("^[\w\-+=\.,\(\)\[\]\{\}';]+$")


def user_db_uri(dbname):
    result = dbname_ptrn.match(dbname)
    if not result:
        raise Exception("Database name is incorrect: {0}".format(dbname))

    home = os.path.expanduser(current_user.home)
    filename = os.path.join(home, "{0}.sqlite".format(dbname))
    return "{0}:///{1}".format('sqlite', filename)


def user_db_exists(dbname):
    dburi = user_db_uri(dbname)
    return database_exists(dburi)

#     result = dbname_ptrn.match(dbname)
#     if not result:
#         raise Exception("Database name is incorrect: {0}".format(dbname))
#
#     home = os.path.expanduser(current_user.home)
#     filename = os.path.join(home, "{0}.sqlite".format(dbname))
#     return os.path.isfile(filename):

#     if not os.path.isfile(filename):
#         raise Exception("Database does not exist: {0}".format(dbname))

""" Creates a context with an open SQLAlchemy session.
"""
@contextmanager
def user_db_session(dbname, create=False):
    dburi = user_db_uri(dbname)

    engine = create_engine(dburi, convert_unicode=True)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))

    yield db_session

    db_session.close()
    connection.close()


@contextmanager
def user_db_session_metadata(dbname, create=False):
    dburi = user_db_uri(dbname)

    engine = create_engine(dburi, convert_unicode=True)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    metadata = MetaData(engine, reflect=True)

    yield db_session, metadata

    db_session.close()
    connection.close()
