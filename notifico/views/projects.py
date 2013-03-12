# -*- coding: utf8 -*-
from flask import render_template

from notifico import app, user_required


@app.route('/dashboard')
@user_required
def projects_dashboard():
    return render_template('projects/dashboard.jinja')
