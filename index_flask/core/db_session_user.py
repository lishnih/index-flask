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


""" Creates a context with an open SQLAlchemy session.
"""

dbname_ptrn = re.compile("^[\w\-+=\.,\(\)\[\]\{\}';]+$")

@contextmanager
def user_db_session(dbname, create=False):
    home = os.path.expanduser(current_user.home)
    result = dbname_ptrn.match(dbname)
    if not result:
        raise Exception("Wrong DB name!")

    filename = os.path.join(home, "{0}.sqlite".format(dbname))
    if not os.path.isfile(filename) and not create:
        raise Exception("DB does not exist: {0}".format(dbname))

    dburi = "{0}:///{1}".format('sqlite', filename)

    engine = create_engine(dburi, convert_unicode=True)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))

    yield db_session

    db_session.close()
    connection.close()


@contextmanager
def user_db_session_metadata(dbname, create=False):
    home = os.path.expanduser(current_user.home)
    result = dbname_ptrn.match(dbname)
    if not result:
        raise Exception("Wrong DB name!")

    filename = os.path.join(home, "{0}.sqlite".format(dbname))
    if not os.path.isfile(filename) and not create:
        raise Exception("DB does not exist: {0}".format(dbname))

    dburi = "{0}:///{1}".format('sqlite', filename)

    engine = create_engine(dburi, convert_unicode=True)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    metadata = MetaData(engine, reflect=True)

    yield db_session, metadata

    db_session.close()
    connection.close()
