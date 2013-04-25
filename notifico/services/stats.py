# -*- coding: utf-8 -*-
"""
A collection of utility methods for common site statistics.
"""
from sqlalchemy import func

from notifico import db, cache
from notifico.models import Project, Channel, User


@cache.memoize(timeout=60 * 5)
def total_messages():
    """
    Sum the total number of messages across all projects.
    """
    total = db.session.query(
        func.sum(Project.message_count)
    ).scalar()

    return total


@cache.memoize(timeout=60 * 5)
def total_users():
    return User.query.count()


@cache.memoize(timeout=60 * 5)
def top_networks(limit=20):
    return (
        db.session.query(
            Channel.host,
            func.count(func.distinct(Channel.channel)).label('count'),
        )
        .join(Channel.project).filter(
            Project.public == True,
            Channel.public == True
        )
        .group_by(Channel.host)
        .order_by('count desc')
        .limit(limit)
    ).all()
