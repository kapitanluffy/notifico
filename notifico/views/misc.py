# -*- coding: utf8 -*-
from flask import (
    render_template
)
from notifico import app, user_required


@app.route('/')
def misc_landing():
    return render_template('misc/landing.jinja')
