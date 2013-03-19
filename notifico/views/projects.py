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
    """
    Presents the user with an overview of their projects and activity.
    """
    per_page = min(int(request.args.get('l', 20)), 100)
    page = max(int(request.args.get('page', 1)), 1)
    sort_by = request.args.get('s', 'created')
    q = request.args.get('q')

    # Search starting from all this user's projects....
    projects_q = g.user.projects
    if q:
        # ... and if a search query was provided, filter down on that...
        projects_q = projects_q.filter(Project.name.like(q + '%'))

    # ... then clear any model-set sorting and sort by whatever
    #     was selected.
    projects_q = projects_q.order_by(False).order_by({
        'created': Project.created.desc(),
        'messages': Project.message_count.desc()
    }.get(sort_by, Project.created.desc()))

    # ... and finally generate the Flask-SQLAlchemy Pagination() object.
    projects = projects_q.paginate(page, per_page, False)

    return render_template('projects/dashboard.jinja', projects=projects)


@app.route('/_/private_search')
@user_required
def projects_private_search():
    """
    Searches for projects starting with the request argument `q`, returning
    a JSON list of [{value: ..., tokens: ...}]. This view only returns
    projects for the currently logged in user.
    """
    q = request.args.get('q', '')
    per_page = min(int(request.args.get('l', 5)), 25)
    page = min(int(request.args.get('page', 1)), 100)

    projects_q = (
        g.user.projects
        .filter(Project.name.like(q + '%'))
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    results = [dict(value=p.name, tokens=[p.name]) for p in projects_q]

    return Response(json.dumps(results),  mimetype='application/json')


@app.route('/new')
@user_required
def projects_new():
    pass
