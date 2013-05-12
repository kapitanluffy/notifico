# -*- coding: utf-8 -*-
__all__ = (
    'ExternalService',
    'URLExternalService',
    'HookExternalService'
)

from jinja2 import Environment, PackageLoader


class _Register(type):
    def __new__(cls, clsname, bases, attrs):
        new_class = super(cls, _Register).__new__(
            cls, clsname, bases, attrs
        )

        if not hasattr(cls, 'registered'):
            cls.registered = {}
        try:
            cls.registered[new_class.service_id()] = new_class
        except NotImplementedError:
            pass

        return new_class


class ExternalService(object):
    """
    Base type for 3rd party service integrations.
    """
    @classmethod
    def service_id(cls):
        """
        A globally unique service identifier as an integer. Used to
        distinguish between service records in the database.
        """
        raise NotImplementedError()

    @classmethod
    def name(cls):
        """
        A human-readable name for this service.
        """
        raise NotImplementedError()

    @classmethod
    def slug(cls):
        """
        A URL-safe, usually short URL slug for this service.
        """
        raise NotImplementedError()

    @classmethod
    def description(cls):
        raise NotImplementedError()

    @classmethod
    def jinja2_env(cls):
        """
        Returns a Jinja2 environment for rendering templates.
        """
        return Environment(
            loader=PackageLoader('notifico.services', 'templates')
        )

    @classmethod
    def form(cls):
        """
        Should return a `wtforms.Form` subclass which will be rendered
        and displayed to the user for service configuration.
        """
        raise NotImplementedError()

    @classmethod
    def validate_form(cls, form, request):
        """
        Returns `True` if the form passes validation, `False` otherwise.
        Should be subclassed by services which require complex
        configuration forms.
        """
        return form.validate_on_submit()

    @classmethod
    def pack_form(cls, form):
        """
        Packs `form` into a dictionary (with the keys being the form
        element IDs and the values being the data).
        """
        return dict((f.id, f.data) for f in form)

    @classmethod
    def unpack_form(cls, config, form=None):
        """
        Unpacks a form previously packed with `pack_form()`.
        """
        if config is None:
            return

        if form is None:
            form = cls.form()

        for f in form:
            if f.id in config:
                f.data = config[f.id]

        return form


class URLExternalService(ExternalService):
    """
    Base type for URL shortener services.
    """
    __metaclass__ = _Register

    @classmethod
    def can_shorten(cls, url_to_shorten):
        """
        When implemented, returns ``True`` if `url_to_shorten` can be
        shortened by this service, ``False`` otherwise. An example is
        Github's `http://git.io` service, which will only shorten
        `http://github.com/.*` URLs.
        """
        raise NotImplementedError()

    @classmethod
    def shorten_url(cls, url_to_shorten):
        """
        Tries to shorten the URL `url_to_shorten`, returning it
        unaltered if unable to do so.
        """
        raise NotImplementedError()


class HookExternalService(ExternalService):
    __metaclass__ = _Register

    @classmethod
    def on_request(cls, hook, request):
        raise NotImplementedError()

    @classmethod
    def absolute_url(cls, hook):
        """
        Returns an absolute URL used as this hooks endpoint if it does
        not use the standard hook-recieve endpoint.
        """
        raise NotImplementedError()

# Must be imported last due to a circular dependency caused by
# self-registration, and so that these services always get registered
# on their base class.
from notifico.services.externals.github import *
