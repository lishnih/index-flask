#!/usr/bin/env python
# coding=utf-8
# Stan 2019-01-17

from __future__ import division, absolute_import, print_function

from flask import current_app

from ..tools.send_email import send_email


def send_csv(user_id, options):
    log = []

    user = User.query.filter_by(id=user_id).first()
    if user:
        filename, error = export_db(user, options, log)
        if error:
            log = [
                "During executing an error has occurred:",
                error,
                "-----"
            ] + log

        log = ''.join(["{0}\n".format(dumb_python(s)) for s in log])
        app.logger.info(log)
        send_email(log, [user.email], filename, [filename])

    else:
        app.logger.error("No user: '{0}'".format(user_id))


def export_db(user, options, log=[]):
    dbname = options.get("dbname", "default")
    output = options.get("output", dbname)
    filename = "~/tmp/{0}.csv".format(output)
    filename = os.path.expanduser(filename)

    # ?????????? DB Uri
    dburi = getUserDbUri(user, options)

    # ????????????? ?????????? ? ??
    engine, session = openDbUri(dburi)
    log.append("Engine: {0}".format(engine))

    sql = options.get("sql")
    if not sql:
        return filename, "SQL required!"

    offset = int(options.get("offset", 0))
    limit = int(options.get("limit", 200000))
    delimiter = options.get("delimiter", ";")
    lineterminator = options.get("lineterminator", "\n")

    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter, lineterminator=lineterminator)

        names_saved = False
        shown = True
        while shown:
            names, rows, total, shown, s = get_rows_plain(session, sql, options=options, offset=offset, limit=limit)

            if not names_saved:
                log.append("Records: {0}".format(total))
                row = [dumb_python(s) for s in names]
                writer.writerow(row)
                names_saved = True

            for row in rows:
                row = [dumb_python(s) for s in row]
                writer.writerow(row)

            offset += limit

    return filename, None


def get_rows_plain(session, sql, options={}, offset=0, limit=None):
    s = select(['*']).select_from(text("({0})".format(sql)))
    s_count = select([func.count()]).select_from(text("({0})".format(sql)))
    total = session.execute(s_count, options).scalar()

    if offset:
        s = s.offset(offset)
    if limit:
        s = s.limit(limit)

    res = session.execute(s, options)
    names = res.keys()

    rows = [[j for j in i] for i in res.fetchall()]

    shown = len(rows)

    return names, rows, total, shown, s
