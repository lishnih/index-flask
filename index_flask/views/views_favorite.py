#!/usr/bin/env python
# coding=utf-8
# Stan 2019-07-12

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from flask import request, redirect, url_for

from flask_login import login_required, current_user

from ..app import app, db
from ..core.db import get_rows_model
from ..core_flask.functions import get_next
from ..core_flask.render_response import render_ext
from ..forms.favorite import AddFavoriteForm
from ..models.favorite import Favorite


# ===== Routes =====

@app.route('/favorites', methods=['GET', 'POST'])
@login_required
def favorites():
    names, rows, total, filtered, shown, page, pages, s = get_rows_model(Favorite, skip_sys=True)

    return render_ext('base.html',
             title = 'Favorites',
             names = names,
             rows = rows,
             total = total,
           )


@app.route('/favorite_add', methods=['GET', 'POST'])
@login_required
def favorite_add():
    message = None
    form = AddFavoriteForm(request.form)

    if request.method == 'POST':
        if form.validate():
            favorite = Favorite(
                name = form.name.data,
                url = form.url.data,
                user = current_user,
            )
            db.session.add(favorite)
            db.session.commit()

            return render_ext("base.html",
                default = redirect(get_next()),
                message = "The page was successfully added",
            )

        else:
            message = "Invalid data!", 'warning'

    return render_ext('favorite/favorite_add.html',
        title = 'Add to favorites',
        message = message,
        form = form,
    )


@app.route("/favorite_delete", methods=['GET', 'POST'])
@login_required
def favorite_delete():
    message = None
    form = AddFavoriteForm(request.form)

    if request.method == 'POST':
        if form.validate():
            #

            return render_ext("base.html",
                default = redirect(get_next()),
                message = "The page successfully added {0}".format(form.favorite.name),
            )

        else:
            message = "Invalid data!", 'warning'

    return render_ext('favorite/favorite_add.html',
        title = 'Delete from favorites',
        message = message,
        form = form,
    )
