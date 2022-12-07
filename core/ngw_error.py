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


class NGWError(Exception):
    TypeUnknownError, TypeRequestError, TypeNGWError, TypeNGWUnexpectedAnswer = list(range(4))

    def __init__(self, type, message, url=None, user_msg=None, need_reconnect=True):
        if not isinstance(message, str):
            self.message = str(message)#, 'utf-8')
        else:
            self.message = message

        self.type = type
        self.url = url
        self.user_msg = user_msg
        self.need_reconnect = need_reconnect

    def __str__(self):
        return self.message

class NoOAuthAuthError(Exception):

    def __init__(self):
        self.message = 'No OAuth authentication'

    def __str__(self):
        return self.message


