# -*- coding: utf8 -*-
from flask import (
    g,
    request,
    render_template
)

from notifico import app, user_required
from notifico.models import Project


@app.route('/dashboard')
@user_required
def projects_dashboard():
    per_page = min(int(request.args.get('l', 10)), 100)
    page = max(int(request.args.get('page', 1)), 1)

    projects = (
        g.user.projects
        .order_by(False)
        .order_by(Project.created.desc())
    ).paginate(page, per_page, False)

    return render_template('projects/dashboard.jinja', projects=projects)
