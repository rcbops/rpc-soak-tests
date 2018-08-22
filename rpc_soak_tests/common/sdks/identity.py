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

from rpc_soak_tests.common.sdks.base import BaseSDK, PROJECTS, USERS


class IdentitySDK(BaseSDK):
    """
    Wrapper for interacting with the openstack identity SDK
    """
    def __init__(self):
        super(IdentitySDK, self).__init__()
        self.client = self.conn.identity

    def get_users(self, project_ids=None, name=None):
        """
        Get the OpenStack cloud users

        :param list project_ids: get only the users within these IDs.
        :param str name: user name prefix or complete name
        :return: list of user(s) that match name, if given, if not all.
        """
        result = self.get_resources(resource_type=USERS,
                                    project_ids=project_ids, name=name)
        return result

    def get_projects(self, project_ids=None, name=None):
        """
        Get the OpenStack cloud projects

        :param list project_ids: get only the projects within these IDs.
        :param str name: project name prefix or complete name.
        :return: list of project(s) that match name, if given, if not all.
        """
        result = self.get_resources(resource_type=PROJECTS,
                                    project_ids=project_ids, name=name)
        return result
