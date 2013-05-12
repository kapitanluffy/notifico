# -*- coding: utf8 -*-
__all__ = ('Hook',)
import os
import base64
import datetime

from notifico import db


class Hook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)
    # A unique API key used to authenticate an incoming request when
    # no other method of authentication is available (for example
    # when the only thing available is a simple WebHook). A key does
    # not need to be globally unique, just unique per project.
    key = db.Column(db.String(255), nullable=False)

    # The total count of messages that have been recieved on this
    # hook, or number of URLs shortened.
    message_count = db.Column(db.Integer, default=0)

    # The identifier for the service associated with this hook.
    service_id = db.Column(db.Integer)
    # The optional configuration for the service associated with
    # this hook.
    config = db.Column(db.PickleType)

    # The project this hook is attached to. While a hook can
    # technically be attached to multiple projects, it should instead
    # be cloned.
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref(
        'hooks', order_by=id, lazy='dynamic', cascade='all, delete-orphan'
    ))

    def __init__(self, *args, **kwargs):
        super(Hook, self).__init__(*args, **kwargs)
        if not self.key:
            self.key = self._new_key()

    @staticmethod
    def _new_key():
        # FIXME: Must check for collisions!
        return base64.urlsafe_b64encode(os.urandom(24))[:24]
