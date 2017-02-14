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
import requests

from os import path
from ngw_resource import NGWResource

from ..utils import ICONS_DIR


class NGWWmsService(NGWResource):

    type_id = 'wmsserver_service'
    icon_path = path.join(ICONS_DIR, 'wms.svg')
    type_title = 'NGW WMS Service'

    def __init__(self, resource_factory, resource_json):
        NGWResource.__init__(self, resource_factory, resource_json)

    @classmethod
    def create_in_group(cls, name, ngw_group_resource, ngw_layers_with_style):
        connection = ngw_group_resource._res_factory.connection
        url = ngw_group_resource.get_api_collection_url()

        params_layers = []
        for ngw_layer, ngw_style_id in ngw_layers_with_style:
            params_layer = dict(
                display_name=ngw_layer.common.display_name,
                keyname="ngw_id_%d" % ngw_layer.common.id,
                resource_id=ngw_style_id,
                min_scale_denom=None,
                max_scale_denom=None,
            )
            params_layers.append(params_layer)

        params = dict(
            resource=dict(
                cls=cls.type_id,
                display_name=name,
                parent=dict(
                    id=ngw_group_resource.common.id
                )
            )
        )

        params[cls.type_id] = dict(
            layers=params_layers
        )

        try:
            result = connection.post(url, params=params)

            ngw_resource = cls(
                ngw_group_resource._res_factory,
                NGWResource.receive_resource_obj(
                    connection,
                    result['id']
                )
            )

            return ngw_resource
        except requests.exceptions.RequestException, e:
            raise NGWError('Cannot create wfs service. Server response:\n%s' % e.message)