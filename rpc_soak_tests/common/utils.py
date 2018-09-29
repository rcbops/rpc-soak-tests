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

from rpc_soak_tests.common.sdks.base import (LOAD_BALANCERS, NETWORKS, PORTS,
                                             PROJECTS, SECURITY_GROUPS,
                                             SERVERS, USERS)
from rpc_soak_tests.common.sdks.base import BaseSDK
from rpc_soak_tests.common.sdks.compute import ComputeSDK
from rpc_soak_tests.common.sdks.identity import IdentitySDK
from rpc_soak_tests.common.sdks.network import NetworkSDK
from rpc_soak_tests.common.sdks.load_balancer import LoadBalancerSDK


DEFAULT_PROJECT_NAME = 'tempest'


class Utils(object):
    """
    Common utilities for interacting with the OpenStack SDK wrappers, for ex.

    from rpc_soak_tests.common.utils import Utils

    # os.environ calls NOT needed if set as env variables
    # See the clouds_example.yaml file to create the clouds.yaml file
    os.environ['OPENSTACK_CLOUD'] = 'deimos_internal'

    # Project to be used by DELETE methods. Not needed if tempest
    # is used since is the default as seen above (this is just an ex.)
    os.environ['PROJECT_NAME'] = 'tempest'

    utils = Utils()
    projects = utils.identity.get_projects()
    networks = utils.network.get_networks()
    undeleted_networks = utils.delete_networks()
    """
    def __init__(self, project_name=None):
        self.base = BaseSDK()
        self.compute = ComputeSDK()
        self.identity = IdentitySDK()
        self.network = NetworkSDK()
        self.loadbalancer = LoadBalancerSDK()

        # Making accesible the OpenStack connection object
        self.conn = self.identity.conn

        # Project name starts with
        self.project_name = (project_name or self.base.config.project_name or
                             DEFAULT_PROJECT_NAME)

    def get_project_ids(self, name=None):
        """
        Get project IDs by name

        :param str name: project name prefix or complete name
        :rtype: list(str)
        :return: list of project IDs
        """
        name = name or self.project_name

        result = self.identity.get_resource_ids(
            resource_type=PROJECTS, name=name)

        return result

    def get_deleted_project_ids(self, name=None):
        """
        Get deleted project IDs by name using existing networks. Sometimes
        tempest resources are left behind, this method will get the tempest
        networks that don't have an existing project anymore and return
        those project IDs.

        :param str name: project and network name prefix
        :rtype: list(str)
        :return: list of project IDs
        """
        name = name or self.project_name

        project_ids = self.get_project_ids(name=name)

        # Using the networks resource to get the deleted project IDs
        networks = self.network.get_networks(name=name)
        deleted_project_ids = []

        for network in networks:
            if network.project_id not in project_ids:
                deleted_project_ids.append(network.project_id)

        return deleted_project_ids

    def get_all_project_ids(self, name=None):
        """
        Get existing and deleted project IDs by name.

        :param str name: project and network name prefix
        :rtype: list(str)
        :return: list of project IDs
        """
        name = name or self.project_name

        result = self.get_project_ids(name=name)
        deleted_project_ids = self.get_deleted_project_ids(name=name)
        result.extend(deleted_project_ids)

        return result

    def delete_servers(self, project_name=None,
                       project_ids=None, server_name=None, query=None,
                       print_delete=True, raise_exception=False, all=False):
        """
        Delete servers filtered by project name, project IDs and/or
        server names. If NOT given the deletes are done by the project IDs
        with the name at the self.project_name attribute.

        :param str project_name: project name to filter by (can be None)
        :param list project_ids: delete only servers within these projects.
        :param str server_name: server name to filter by.
        :param dict query: additional kwargs for delete filters
            (GET resources call).
        :param bool print_delete: print the resource name and ID.
        :param bool raise_exception: flag to raise an Exception if True.
        :param bool all: delete ALL resources found (ignores project ids/name)
        :return: list of undeleted servers(s)
        """
        if not project_ids and not server_name and not query:
            project_name = project_name or self.project_name
            project_ids = self.get_all_project_ids(name=project_name)

        result = self.compute.delete_resources(
            resource_type=SERVERS, project_ids=project_ids, name=server_name,
            query=query, print_delete=print_delete,
            raise_exception=raise_exception, all=all)

        return result

    def delete_rally_servers(self, server_name='s_rally'):
        """
        Delete servers from all tenants
        :param str server_name: server name starts with, by default s_rally.
        :return: list of undeleted servers(s)

        """

        query = dict(all_tenants=True, name='s_rally')
        result = self.delete_servers(query=query, all=True)

        return result

    def delete_networks(self, project_name=None,
                        project_ids=None, network_name=None,
                        print_delete=True, raise_exception=False):
        """
        Delete networks filtered by project name, project IDs and/or
        network names. If NOT given the deletes are done by the project IDs
        with the name at the self.project_name attribute.

        :param str project_name: project name to filter by (can be None)
        :param list project_ids: delete only networks within these projects.
        :param str network_name: network name to filter by.
        :param bool print_delete: print the resource name and ID.
        :param bool raise_exception: flag to raise an Exception if True.
        :return: list of undeleted network(s)
        """
        if not project_ids and not network_name:
            project_name = project_name or self.project_name
            project_ids = self.get_all_project_ids(name=project_name)

        result = self.network.delete_resources(
            resource_type=NETWORKS, project_ids=project_ids, name=network_name,
            print_delete=print_delete, raise_exception=raise_exception)

        return result

    def delete_ports(self, project_name=None, project_ids=None,
                     port_name=None, print_delete=True, raise_exception=False):
        """
        Delete ports filtered by project name, project IDs and/or
        port names. If NOT given the deletes are done by the project IDs
        with the name at the self.project_name attribute.

        :param str project_name: project name to filter by (can be None)
        :param list project_ids: delete only ports within these projects.
        :param str port_name: port name to filter by.
        :param bool print_delete: print the resource name and ID.
        :param bool raise_exception: flag to raise an Exception if True.
        :return: list of undeleted port(s)
        """
        if not project_ids and not port_name:
            project_name = project_name or self.project_name
            project_ids = self.get_all_project_ids(name=project_name)

        result = self.network.delete_resources(
            resource_type=PORTS, project_ids=project_ids, name=port_name,
            print_delete=print_delete, raise_exception=raise_exception)

        return result

    def delete_security_groups(self, project_name=None,
                               project_ids=None, sec_group_name=None,
                               print_delete=True, raise_exception=False):
        """
        Delete sec groups filtered by project name, project IDs and/or
        sec group names. If NOT given the deletes are done by the project IDs
        with the name at the self.project_name attribute.

        Default security groups need to be deleted after their project is
        deleted and they will need to be targeted by the deleted project ID
        or name.

        :param str project_name: project name to filter by (can be None)
        :param list project_ids: delete only ports within these projects.
        :param str sec_group_name: security group name to filter by.
        :param bool print_delete: print the resource name and ID.
        :param bool raise_exception: flag to raise an Exception if True.
        :return: list of undeleted security groups(s)
        """
        if not project_ids and not sec_group_name:
            project_name = project_name or self.project_name
            project_ids = self.get_all_project_ids(name=project_name)

        result = self.network.delete_resources(
            resource_type=SECURITY_GROUPS, project_ids=project_ids,
            name=sec_group_name, print_delete=print_delete,
            raise_exception=raise_exception)

        return result

    def delete_load_balancers(self, project_name=None,
                              project_ids=None, lb_name=None,
                              print_delete=True, raise_exception=False):
        """
        Delete lbs filtered by project name, project IDs and/or
        lb names. If NOT given the deletes are done by the project IDs
        with the name at the self.project_name attribute.

        :param str project_name: project name to filter by (can be None)
        :param list project_ids: delete only lbs within these projects.
        :param str lb_name: loadbalancer name to filter by.
        :param bool print_delete: print the resource name and ID.
        :param bool raise_exception: flag to raise an Exception if True.
        :return: list of undeleted load balancers(s)
        """
        if not project_ids and not lb_name:
            project_name = project_name or self.project_name
            project_ids = self.get_all_project_ids(name=project_name)

        result = self.loadbalancer.delete_resources(
            resource_type=LOAD_BALANCERS, project_ids=project_ids,
            name=lb_name, print_delete=print_delete,
            raise_exception=raise_exception)

        return result

    def delete_projects(self, name=None, print_delete=True,
                        raise_exception=False):
        """
        Delete projects filtered by project name. ID is an invalid query
        param for projects so the project_ids param can not be used here.

        :param str name: project name to filter by (can be None)
        :param bool print_delete: print the resource name and ID.
        :param bool raise_exception: flag to raise an Exception if True.
        :return: list of undeleted projects(s)
        """
        name = name or self.project_name

        result = self.identity.delete_resources(
            resource_type=PROJECTS, name=name, print_delete=print_delete,
            raise_exception=raise_exception)

        return result

    def delete_users(self, project_name=None,
                     project_ids=None, user_name=None,
                     print_delete=True, raise_exception=False):
        """
        Delete users filtered by project name, project IDs and/or
        user names. If NOT given the deletes are done by the project IDs
        with the name at the self.project_name attribute.

        :param str project_name: project name to filter by (can be None)
        :param list project_ids: delete only users within these projects.
        :param str user_name: user name to filter by.
        :param bool print_delete: print the resource name and ID.
        :param bool raise_exception: flag to raise an Exception if True.
        :return: list of undeleted user(s)
        """
        if not project_ids and not user_name:
            project_name = project_name or self.project_name
            project_ids = self.get_all_project_ids(name=project_name)

        result = self.identity.delete_resources(
            resource_type=USERS, project_ids=project_ids,
            name=user_name, print_delete=print_delete,
            raise_exception=raise_exception)

        return result
