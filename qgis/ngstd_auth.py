# -*- coding: utf-8 -*-

from ..utils import log

HAS_NGSTD = False
try:
    from ngstd.core import *
    from ngstd.framework import *
    HAS_NGSTD = True
except:
    log(u'Failed to import NgStd. The OAuth2 authentication is disabled')


class NgStd:

    # @classmethod
    # def has_ngstd(cls):
    #     return HAS_NGSTD

    @classmethod
    def instance(cls):
        return NGAccess.instance()

    @classmethod
    def add_auth_url(cls, endpoint):
        try:
            ok = NGRequest.addAuthURL(NGAccess.instance().endPoint(), endpoint)
            if ok:
                log(u'Successfully added auth URL "{}" to NgStd'.format(endpoint))
            else:
                log(u'Unable to add auth URL to NgStd: returned False')
        except:
            log(u'Failed to add auth URL to NgStd: exception')

    @classmethod
    def has_auth(cls):
        try:
            return NGAccess.instance().isUserAuthorized()
        except:
            log(u'Failed to check whether user is authorized')
            return False


    @classmethod
    def get_auth_header(cls):
        try:
            header = NGRequest.getAuthHeader(NGAccess.instance().endPoint())
            log(u'Successfully get oauth header')
            return header
        except:
            log(u'Failed to get oauth header')
            return None



