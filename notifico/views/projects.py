# -*- coding: utf8 -*-
import json

from flask import (
    g,
    request,
    render_template,
    Response
)

from notifico import app, user_required
from notifico.models import Project


@app.route('/dashboard')
@user_required
def projects_dashboard():
    per_page = min(int(request.args.get('l', 20)), 100)
    page = max(int(request.args.get('page', 1)), 1)
    q = request.args.get('q')

    # Search starting from all this users projects....
    projects = g.user.projects
    if q:
        # ... and if a search query was provided, filter down on that...
        projects = projects.filter(Project.name.like(q + '%'))

    projects = projects.order_by(False).order_by(Project.created.desc())
    projects = projects.paginate(page, per_page, False)

    return render_template('projects/dashboard.jinja', projects=projects)


@app.route('/_/private_search')
@user_required
def projects_private_search():
    q = request.args.get('q')

    results = [{
        'value': p.name,
        'tokens': [p.name]
    } for p in g.user.projects if p.name.lower().startswith(q.lower())]

    return Response(json.dumps(results),  mimetype='application/json')


@app.route('/new')
@user_required
def projects_new():
    pass
