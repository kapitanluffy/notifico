from flask import (
    Blueprint,
    render_template
)

from notifico.models import Project
from notifico.services import stats

public = Blueprint('public', __name__, template_folder='templates')


@public.route('/')
def landing():
    """
    Show a landing page giving a short intro blurb to unregistered
    users.
    """
    recent_projects = (
        Project.query
        .filter_by(public=True)
        .order_by(Project.created.desc())
        .limit(10)
    )

    return render_template(
        'landing.html',
        recent_projects=recent_projects,
        top_networks=stats.top_networks(limit=10)
    )


@public.route('/faq')
def faq():
    """
    Shows a simple FAQ listing.
    """
    return render_template('faq.html')
