#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-08

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker


""" Creates a context with an open SQLAlchemy session.
"""

@contextmanager
def db_session(dburi):
    engine = create_engine(dburi, convert_unicode=True)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))

    yield db_session

    db_session.close()
    connection.close()


@contextmanager
def db_session_metadata(dburi):
    engine = create_engine(dburi, convert_unicode=True)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    metadata = MetaData(engine, reflect=True)

    yield db_session, metadata

    db_session.close()
    connection.close()
