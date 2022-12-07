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

    @classmethod
    def instance(cls):
        return NGAccess.instance()

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



