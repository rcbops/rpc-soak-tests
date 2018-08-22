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

from rpc_soak_tests.common.sdks.base import BaseSDK, LOAD_BALANCERS


class LoadBalancerSDK(BaseSDK):
    """
    Wrappers for interacting with the OpenStack Load Balancer SDK
    """
    def __init__(self):
        super(LoadBalancerSDK, self).__init__()
        self.client = self.conn.load_balancer

    def get_load_balancers(self, project_ids=None, name=None):
        """
        Get the OpenStack cloud load balancers

        :param list project_ids: get only networks within these projects.
        :param str name: lb name prefix or complete name.
        :rtype: list(LoadBalancer)
        :return: list of load balancer(s).
        """
        result = self.get_resources(resource_type=LOAD_BALANCERS,
                                    project_ids=project_ids, name=name)
        return result
