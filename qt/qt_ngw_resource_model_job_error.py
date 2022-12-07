# -*- coding: utf-8 -*-
"""
/***************************************************************************
    NextGIS WEB API
                              -------------------
        begin                : 2014-11-19
        git sha              : $Format:%H$
        copyright            : (C) 2014 by NextGIS
        email                : info@nextgis.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

class NGWResourceModelJobError(Exception):
    """Common error"""
    def __init__(self, msg):
        super(NGWResourceModelJobError, self).__init__()
        self.msg = msg
        self.user_msg = None

    def __str__(self):
        return self.msg

class JobError(NGWResourceModelJobError):
	"""Specific job error"""
	def __init__(self, msg, wrapped_exception=None):
		super(JobError, self).__init__(msg)
		self.wrapped_exception = wrapped_exception

class JobWarning(NGWResourceModelJobError):
	"""Specific job warning"""
	def __init__(self, msg ):
		super(JobWarning, self).__init__(msg)

class JobInternalError(NGWResourceModelJobError):
	"""Unexpected job error. With trace"""
	def __init__(self, msg, trace):
		super(JobInternalError, self).__init__(msg)
		self.trace = trace

class JobServerRequestError(NGWResourceModelJobError):
	"""Something wrong with request to NGW like  no connection, 502, ngw error """
	def __init__(self, msg, url, user_msg=None, need_reconnect=True):
		super(JobServerRequestError, self).__init__(msg)
		self.url = url
		self.user_msg = user_msg
		self.need_reconnect = need_reconnect

class JobNGWError(JobServerRequestError):
	"""NGW answer is received, but NGW cann't execute request for perform the job"""
	def __init__(self, msg, url):
		super(JobNGWError, self).__init__(msg, url)


class JobAuthorizationError(JobNGWError):
	"""NGW cann't execute request for perform the job because user does not have rights"""
	def __init__(self, url):
		super(JobAuthorizationError, self).__init__("", url)

class JobNoOAuthAuthError(NGWResourceModelJobError):
	def __init__(self, msg):
		super(JobNoOAuthAuthError, self).__init__(msg)

