# -*- coding: utf8 -*-
__all__ = ('Project',)
import datetime

from sqlalchemy import or_
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from notifico import db
from notifico.models import CaseInsensitiveComparator


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)
    public = db.Column(db.Boolean, default=True)
    website = db.Column(db.String(1024))

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref=db.backref(
        'projects', order_by=id, lazy='dynamic', cascade='all, delete-orphan'
    ))

    full_name = db.Column(db.String(101), nullable=False, unique=True)
    message_count = db.Column(db.Integer, default=0)

    @hybrid_property
    def name_i(self):
        return self.name.lower()

    @name_i.comparator
    def name_i(cls):
        return CaseInsensitiveComparator(cls.name)

    @classmethod
    def by_name(cls, name):
        return cls.query.filter_by(name_i=name).first()

    @classmethod
    def by_name_and_owner(cls, name, owner):
        q = cls.query.filter(cls.owner_id == owner.id)
        q = q.filter(cls.name_i == name)
        return q.first()

    def is_owner(self, user):
        """
        Returns ``True`` if `user` is the owner of this project.
        """
        return user and user.id == self.owner.id

    def can_modify(self, user):
        """
        Returns ``True`` if `user` can modify this project.
        """
        # Admins can always modify projects.
        if user and user.in_group('admin'):
            return True

        if user and user.id == self.owner.id:
            return True

        return False

    @classmethod
    def visible_projects(cls, user=None):
        q = cls.query

        if user and user.in_group('admin'):
            # Admins always have full visibility.
            pass
        elif user:
            # If there's a logged in user, he can see all of his
            # own projects and other user's public projects.
            q = q.filter(or_(
                Project.owner_id == user.id,
                Project.public == True
            ))
        else:
            q = q.filter(Project.public == True)

        return q

    @validates('website')
    def validates_website(self, key, website):
        return website.strip() if website else website
