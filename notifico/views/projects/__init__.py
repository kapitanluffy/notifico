# -*- coding: utf-8 -*_
from flask import (
    Blueprint,
    render_template,
    g,
    redirect,
    url_for,
    abort,
    flash
)
from flask.ext import wtf

from notifico import user_required, db
from notifico.models import Project, User
from notifico.services.stats import total_messages

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
            # TODO: Go directly to project details page.
            return redirect(
                url_for('.user_projects', username=user.username)
            )

    return render_template(
        'new_project.html',
        form=form,
        user=user
    )
