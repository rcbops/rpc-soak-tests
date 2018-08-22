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

from rpc_soak_tests.common.sdks.base import BaseSDK, SERVERS


class ComputeSDK(BaseSDK):
    """
    Wrapper for interacting with the OpenStack compute SDK
    """
    def __init__(self):
        super(ComputeSDK, self).__init__()
        self.client = self.conn.compute

    def get_servers(self, project_ids=None, name=None):
        """
        Get the OpenStack cloud servers

        :param list project_ids: get only servers within these projects.
        :param str name: server name prefix or complete name.
        :rtype: list(ServerDetail)
        :return: list of servers(s).
        """
        result = self.get_resources(resource_type=SERVERS,
                                    project_ids=project_ids, name=name)
        return result
