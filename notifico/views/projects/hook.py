# -*- coding: utf-8 -*-
from flask import (
    g,
    flash,
    abort,
    request,
    url_for,
    redirect,
    render_template
)

from notifico import db, user_required
from notifico.models import Hook, Project, User
from notifico.views.projects import projects
from notifico.services.hooks import HookService


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

    db.session.commit()
    return ''


@projects.route('/<username>/<projectname>/hook/new/', defaults={
    'serviceid': 10
}, methods=['GET', 'POST'])
@projects.route(
    '/<username>/<projectname>/hook/new/<int:serviceid>',
    methods=['GET', 'POST']
)
@user_required
def hook_new(username, projectname, serviceid):
    """
    Allows a user to create a new project hook for `username`, assuming
    they have permission to do so.
    """
    user = User.by_username(username) if username else g.user

    if user is None:
        return abort(404)

    if not user.can_modify(g.user):
        flash(
            'You cannot create new hooks for this user.',
            category='error'
        )
        return redirect(url_for('public.landing'))

    project = Project.by_name_and_owner(projectname, user)
    if project is None:
        return abort(404)

    if not project.can_modify(g.user):
        flash(
            'You cannot create new hooks for this project.',
            category='error'
        )
        return redirect(url_for('public.landing'))

    # Find the service the user is trying to create a hook
    # for.
    hook = HookService.services.get(serviceid)
    if hook is None:
        flash(
            'There is no such hook service.',
            category='error'
        )
        return redirect(
            url_for(
                '.hook_new',
                username=user.username,
                projectname=project.name
            )
        )

    # Check to see if that service implements a configuration form.
    form = hook.form()
    if form:
        form = form()

    return render_template(
        'hook/new.html',
        user=user,
        project=project,
        services=HookService.services,
        form=form,
        service=hook
    )
