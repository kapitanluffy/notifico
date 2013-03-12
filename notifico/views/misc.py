# -*- coding: utf8 -*-
from flask import (
    g,
    redirect,
    url_for,
    render_template
)
from notifico import app


@app.route('/')
def misc_landing():
    if g.user:
        return redirect(url_for('projects_dashboard'))

    return render_template('misc/landing.jinja')
