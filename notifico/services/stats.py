# -*- coding: utf-8 -*-
"""
A collection of utility methods for common site statistics.
"""
from flask import current_app, g
from sqlalchemy import func

from notifico import db
from notifico.models import Project, Channel


def total_messages(cache=False, timeout=60 * 5):
    """
    Sum the total number of messages across all projects.
    """
    if cache:
        total = current_app.get('message_total')
        if total is not None:
            return total

    total = db.session.query(
        func.sum(Project.message_count)
    ).scalar()

    if cache:
        cache.set('message_total', total, timeout=timeout)

    return total


def top_networks():
    return (
        Channel.visible(db.session.query(
            Channel.host,
            func.count(func.distinct(Channel.channel)).label('count')
        ), user=g.user)
        .group_by(Channel.host)
        .order_by('count desc')
    )
