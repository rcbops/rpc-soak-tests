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

from rpc_soak_tests.common.sdks.base import (BaseSDK, NETWORKS, PORTS,
                                             SECURITY_GROUPS)


class NetworkSDK(BaseSDK):
    """
    Wrapper for interacting with the openstack network SDK
    """
    def __init__(self):
        super(NetworkSDK, self).__init__()
        self.client = self.conn.network

    def get_networks(self, project_ids=None, name=None):
        """
        Get the OpenStack cloud networks

        :param list project_ids: get only networks within these projects.
        :param str name: network name prefix or complete name.
        :rtype: list(Network)
        :return: list of networks(s).
        """
        result = self.get_resources(resource_type=NETWORKS,
                                    project_ids=project_ids, name=name)
        return result

    def get_ports(self, project_ids=None, name=None):
        """
        Get the OpenStack cloud ports

        :param list project_ids: get only ports within these projects.
        :param str name: port name prefix or complete name
        :rtype: list(PORT)
        :return: list of ports(s).
        """
        result = self.get_resources(resource_type=PORTS,
                                    project_ids=project_ids, name=name)
        return result

    def get_security_groups(self, project_ids=None, name=None):
        """
        Get the OpenStack cloud security_groups

        :param list project_ids: get only security groups within these projects
        :param str name: security_group name prefix or complete name
        :rtype: list(SecurityGroup)
        :return: list of security_groups(s)
        """
        result = self.get_resources(resource_type=SECURITY_GROUPS,
                                    project_ids=project_ids, name=name)
        return result
