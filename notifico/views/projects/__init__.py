# -*- coding: utf-8 -*_
from flask import (
    Blueprint,
    render_template,
    g,
    redirect,
    url_for,
    abort
)

from notifico import user_required
from notifico.models import Project, User
from notifico.services.stats import total_messages

projects = Blueprint('projects', __name__, template_folder='templates')


@projects.route('/my-projects')
@user_required
def my_projects():
    """
    Redirects the user to their projects page.
    """
    return redirect(url_for(
        '.user_projects', username=g.user.username
    ))


@projects.route('/<username>/')
def user_projects(username):
    user = User.by_username(username)
    if user is None:
        return abort(404)

    projects = (
        user.projects
        .order_by(None)
        .order_by(Project.created.desc())
    )

    if not user.can_modify(g.user):
        projects = projects.filter_by(public=True)

    messages = total_messages(user=user)

    return render_template(
        'my_projects.html',
        user=user,
        projects=projects,
        total_messages=messages,
        can_modify=user.can_modify(g.user)
    )
