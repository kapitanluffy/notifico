# -*- coding: utf-8 -*_
from flask import (
    Blueprint,
    render_template,
    g,
    redirect,
    url_for,
    abort,
    flash,
    request
)
from flask.ext import wtf

from notifico import user_required, db
from notifico.models import Project, User, Hook
from notifico.services.stats import total_messages
from notifico.services.hooks import HookService

projects = Blueprint('projects', __name__, template_folder='templates')


class ProjectDetailsForm(wtf.Form):
    name = wtf.TextField('Project Name', validators=[
        wtf.Required(),
        wtf.Length(1, 50),
        wtf.Regexp(r'^[a-zA-Z0-9_\-\.]*$', message=(
            'Project name must only contain a to z, 0 to 9, dashes'
            ', periods and underscores.'
        ))
    ])
    public = wtf.BooleanField('Public', validators=[
    ], default=True, description=(
        'Public projects are visible to anyone, although you can hide'
        ' individual channels.'
    ))
    website = wtf.TextField('Project URL', validators=[
        wtf.Optional(),
        wtf.Length(max=1024),
        wtf.validators.URL()
    ], description=(
        'A link that will be displayed beside your projects, such'
        ' as a homepage or code repo.'
    ))


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
    """
    Provides an overview of a user and their projects.
    """
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


@projects.route('/<username>/<projectname>')
def user_project(username, projectname):
    """
    Provides an overview of a single user project.
    """
    user = User.by_username(username)
    if user is None:
        return abort(404)

    project = Project.by_name_and_owner(projectname, user)
    if project is None:
        return abort(404)

    if not project.can_see(g.user):
        return redirect(url_for('public.landing'))

    # Make sure only channels the user should be able to see are
    # shown.
    can_modify = project.can_modify(g.user)
    visible_channels = project.channels
    if not can_modify:
        visible_channels = visible_channels.filter_by(public=True)

    return render_template(
        'user_project.html',
        user=user,
        project=project,
        can_modify=can_modify,
        channels=visible_channels
    )


@projects.route('/new/project', methods=['GET', 'POST'])
@projects.route('/new/project/<username>', methods=['GET', 'POST'])
@user_required
def new_project(username=None):
    """
    Allows a user to create a new project for `username`, assuming
    they have permission to do so.
    """
    user = User.by_username(username) if username else g.user

    if user is None:
        return abort(404)

    if not user.can_modify(g.user):
        flash(
            'You cannot create new projects for this user.',
            category='error'
        )
        return redirect(url_for('public.landing'))

    form = ProjectDetailsForm()
    if form.validate_on_submit():
        existing_project = Project.by_name_and_owner(
            form.name.data,
            user
        )
        if existing_project:
            form.name.errors = [
                wtf.ValidationError(
                    'Your project name must be unique, you already'
                    ' have a project called {name}.'.format(
                        name=form.name.data
                    )
                )
            ]
        else:
            # There's no existing project by this name, so we can
            # go ahead and create it.
            p = Project(
                name=form.name.data,
                public=form.public.data,
                website=form.website.data
            )
            # Pre-cache the "full" project name so we can use it for
            # autocompletion later without having to do a JOIN
            # on the owner (to get the username).
            p.full_name = '{username}/{project_name}'.format(
                username=user.username,
                project_name=p.name
            )
            # And add this new project to the user it was created for.
            user.projects.append(p)
            # And save it.
            db.session.commit()
            # TODO: Support Channel Lists.
            # TODO: Go directly to project details page.
            return redirect(
                url_for('.user_projects', username=user.username)
            )

    return render_template(
        'new_project.html',
        form=form,
        user=user
    )


@projects.route('/h/<int:pid>/<key>', methods=['GET', 'POST'])
def hook_receive(pid, key):
    """
    Endpoint for Hook requests from outside parties.
    """
    # TODO: Check referer?
    h = Hook.query.filter_by(key=key, project_id=pid).first()
    if not h or not h.project:
        # The hook being pushed to doesn't exist, has been deleted,
        # or is a leftover from a project cull (which destroyed the project
        # but not the hooks associated with it).
        return abort(404)

    # Increment the hooks message_count....
    Hook.query.filter_by(id=h.id).update({
        Hook.message_count: Hook.message_count + 1
    })
    # ... and the project-wide message_count.
    Project.query.filter_by(id=h.project.id).update({
        Project.message_count: Project.message_count + 1
    })

    hook = HookService.services.get(h.service_id)
    if hook is None:
        # TODO: This should be logged somewhere.
        return ''

    hook._request(h.project.owner, request, h)

    g.db.session.commit()
    return ''
