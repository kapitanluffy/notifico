from flask import (
    Blueprint,
    render_template
)

from notifico.models import User, Project
from notifico.services import stats

public = Blueprint('public', __name__, template_folder='templates')


@public.route('/')
def landing():
    """
    Show a landing page giving a short intro blurb to unregistered
    users.
    """
    total_messages = stats.total_messages()
    total_users = User.query.count()
    total_projects = Project.query.count()

    recent_projects = (
        Project.query
        .filter_by(public=True)
        .order_by(Project.created.desc())
        .limit(20)
    )

    return render_template(
        'landing.html',
        total_messages=total_messages,
        total_users=total_users,
        total_projects=total_projects,
        recent_projects=recent_projects,
        top_networks=stats.top_networks().limit(20)
    )
