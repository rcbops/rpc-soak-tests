"""
Copyright 2018 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from rpc_soak_tests.common.exceptions import InvalidTypeException
from rpc_soak_tests.common.sdks.base import BaseSDK, SERVERS


class ComputeSDK(BaseSDK):
    """
    Wrapper for interacting with the OpenStack compute SDK
    """
    def __init__(self):
        super(ComputeSDK, self).__init__()
        self.client = self.conn.compute

    def get_servers(self, project_ids=None, name=None, details=False,
                    query=None):
        """
        Get the OpenStack cloud servers

        :param list project_ids: get only servers within these projects.
        :param str name: server name prefix or complete name.
        :param bool details: type of server instances returned, for ex.
           if True openstack.compute.v2.server.ServerDetail
           if False openstack.compute.v2.server.Server (used by deletes)
        :param dict query: additional server kwargs for the GET call. For ex.
            image, flavor, name (takes regular expressions), status and host.
        :rtype: list(Server) or list(ServerDetail) if details=True in query
        :return: list of servers(s).
        """

        if not query:
            query = dict()
        else:
            query_type = type(query)
            if query_type != dict:
                msg = 'Expecting a dict instead of {0} for query'.format(
                    query_type)
                raise InvalidTypeException(msg)

        query.update(details=details)
        result = self.get_resources(
            resource_type=SERVERS, project_ids=project_ids, name=name,
            query=query)
        return result
