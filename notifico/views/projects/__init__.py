# -*- coding: utf-8 -*_
from flask import (
    Blueprint,
    render_template,
    g
)

from notifico import user_required
from notifico.models import Project

projects = Blueprint('projects', __name__, template_folder='templates')


@projects.route('/my-projects')
@user_required
def my_projects():
    user = g.user
    projects = (
        user.projects
        .order_by(None)
        .order_by(Project.created.desc())
    )

    return render_template(
        'my_projects.html',
        projects=projects
    )
