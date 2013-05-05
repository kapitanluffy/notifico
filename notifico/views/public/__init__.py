from flask import (
    Blueprint,
    render_template,
    request,
    g
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
        top_networks=stats.top_networks(limit=10),
        total_projects=stats.total_projects()
    )


@public.route('/faq')
def faq():
    """
    Shows a simple FAQ listing.
    """
    return render_template('faq.html')


@public.route('/p/projects', defaults={'page': 1})
@public.route('/s/projects/<int:page>')
def all_projects(page=1):
    per_page = min(int(request.args.get('l', 25)), 100)
    sort_by = request.args.get('s', 'created')

    q = Project.visible_projects(g.user)
    q = q.order_by(False)
    q = q.order_by({
        'created': Project.created.desc(),
        'messages': Project.message_count.desc()
    }.get(sort_by, Project.created.desc()))

    pagination = q.paginate(page, per_page, False)

    return render_template(
        'all_projects.html', pagination=pagination, per_page=per_page
    )
