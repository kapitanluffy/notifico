# -*- coding: utf-8 -*-
__all__ = ('GithubURLService',)
import re

import requests
from flask import current_app

from notifico.services.external import (
    URLExternalService,
    HookExternalService
)


class GithubURLService(URLExternalService):
    @classmethod
    def service_id(cls):
        return 10

    @classmethod
    def name(cls):
        return 'git.io'

    @classmethod
    def slug(cls):
        return 'github'

    @classmethod
    def can_shorten(cls, url_to_shorten):
        # git.io will only shorten Github domains.
        if re.seach(r'^https?://github.(com|io)', url_to_shorten):
            return True
        return False

    @classmethod
    def shorten_url(cls, url_to_shorten):
        try:
            r = requests.post('http://git.io', data={
                'url': url_to_shorten
            }, timeout=4.0)
        except requests.exceptions.Timeout:
            return url_to_shorten

        # Something went wrong, usually means we're being throttled.
        # TODO: If we are being throttled, handle this smarter instead
        #       of trying again on the next message.
        if r.status_code != 201:
            return url_to_shorten

        return r.headers['Location']


class GithubHookService(HookExternalService):
    @classmethod
    def service_id(cls):
        return 10

    @classmethod
    def name(cls):
        return 'Github'

    @classmethod
    def slug(cls):
        return 'github'

    @classmethod
    def on_request(cls, hook, request):
        pass

    @classmethod
    def description(cls):
        return ''
