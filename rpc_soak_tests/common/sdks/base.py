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

import openstack

from rpc_soak_tests.common.config import Config
from rpc_soak_tests.common.exceptions import (MissingDeleteParams,
                                              UnableToDeleteResource)


# resource types
LOAD_BALANCERS = 'load_balancers'
NETWORKS = 'networks'
PORTS = 'ports'
PROJECTS = 'projects'
SECURITY_GROUPS = 'security_groups'
SERVERS = 'servers'
USERS = 'users'

# resource_type is in plural, this dict should provide singular forms
SINGULAR = dict(load_balancers='load_balancer', networks='network',
                ports='port', projects='project',
                security_groups='security_group', servers='server',
                users='user')


class BaseSDK(object):
    """
    Base class for the SDK openstack wrappers
    These methods are to be called by child classes, SDKs, that define the
    self.client attribute.
    """
    def __init__(self, config_variables=None):
        """
        :param list(str) config_variables: list of environment variable names
            for the self.config object. If not given defaults from the Config
            module will be used.
        """
        self.config = Config(variables=config_variables)
        self.conn = openstack.connect(cloud=self.config.openstack_cloud)

    def get_project_id_label(self, resource_type):
        """
        Gets the project ID label for the resource type. For ex. a user object
        has the attribute default_project_id but a project object has only
        the attribute id while all the others, or most, have the project_id
        attribute name for their corresponding project ID.

        :param str resource_type: users, projects, networks, servers, etc.
        :rtype: str
        :return: project ID attribute label of the resource_type object
        """
        if resource_type in ['users']:
            project_id_label = 'default_project_id'
        elif resource_type in ['projects']:
            project_id_label = 'id'
        else:
            project_id_label = 'project_id'

        return project_id_label

    def get_resource_ids(self, resource_type, project_ids=None, name=None):
        """
        Get resource IDs.

        :param str resource_type: resources to get, for ex. loadbalancers,
            networks, users, projects, etc.
        :param list project_ids: only get resources within these projects.
            NOT to be used if the resource_type is projects since it's
            redundant and throws an invalid query param.
        :param str name: name prefix or complete name
        :rtype: list(str)
        :return: list of resource IDs.
        """
        resources = self.get_resources(resource_type=resource_type,
                                       project_ids=project_ids, name=name)

        result = []
        for resource in resources:
            result.append(resource.id)

        return result

    def get_resources(self, resource_type, project_ids=None, name=None,
                      query=None):
        """
        Get OpenStack resources within projects, with names or ALL.

        :param str resource_type: resources to get, for ex. loadbalancers,
            networks, users, projects, etc.
        :param list project_ids: only get resources within these projects.
        :param str name: name prefix or complete name
        :param dict query: additional kwargs for the GET call.
        :rtype: list(openstack resource instance)
        :return: list of resources within the projects given and/or
            that match name (all if project_ids and name not given).
        """
        resources = []

        if project_ids:
            project_id_label = self.get_project_id_label(resource_type)

            for project_id in project_ids:
                kwargs = {project_id_label: project_id}
                if query:
                    kwargs.update(query)
                resp = getattr(self.client, resource_type)(**kwargs)
                resources.extend(list(resp))
        elif query:
            resp = getattr(self.client, resource_type)(**query)
            resources.extend(list(resp))
        else:
            resp = getattr(self.client, resource_type)()
            resources.extend(list(resp))

        if not name:
            result = resources
        else:
            result = []
            for resource in resources:
                if resource.name.startswith(name):
                    result.append(resource)

        return result

    def delete_resources(self, resource_type, project_ids=None, name=None,
                         query=None, print_delete=False,
                         raise_exception=False, all=False):
        """
        Delete OpenStack resources within projects, by name or All.

        :param str resource_type: resources to get, for ex. loadbalancers,
            networks, users, projects, etc.
        :param list project_ids: only get resources within these projects.
        :param str name: name(starts with) to filter resources to delete.
        :param dict query: additional kwargs for the GET resources call.
        :param bool print_delete: print the resource name and ID.
        :param bool raise_exception: flag to raise an Exception if True.
        :param bool all: if set and no project_ids or name given it will try
            to delete ALL resources (use with caution).
        :rtype: dict
        :return: list of undeleted resources.
        :raises: UnableToDeleteResource exception if raise_exception True.
        """

        if not project_ids and not name and not all:
            msg = ('Project IDs or resource names are missing and needed for '
                   'deleting OpenStack cloud resources.')
            raise MissingDeleteParams(msg)

        kwargs = dict(resource_type=resource_type, project_ids=project_ids,
                      name=name)

        # Need the server.Server instance for deleting servers (these
        # instances don't have the project ID, None will be displayed in msgs)
        if not query:
            query = dict()
        if resource_type==SERVERS:
            query.update(details=False)

        kwargs.update(query=query)
        resources = self.get_resources(**kwargs)

        # singular resource type name, for ex. network, port, etc.
        type_name = SINGULAR[resource_type]
        delete_fn = 'delete_{0}'.format(type_name)
        undeleted_resources = []
        project_id_label = None

        if print_delete:
            project_id_label = self.get_project_id_label(resource_type)

        for resource in resources:
            try:
                resp = getattr(self.client, delete_fn)(resource)
                if print_delete:
                    project_id = getattr(resource, project_id_label)
                    msg = ('Deleted {0} {1} with ID {2} from project '
                           '{3}').format(type_name, resource.name,
                                         resource.id, project_id)
                    print(msg)
            except Exception as e:
                if raise_exception:
                    raise UnableToDeleteResource(e.message)
                else:
                    undeleted_resources.append(resource.id)
                    if print_delete:
                        project_id = getattr(resource, project_id_label)
                        msg = ('Unable to delete {0} {1} with ID {2} from '
                               'project {3}').format(type_name, resource.name,
                                                     resource.id, project_id)
                        print(msg)

        return undeleted_resources
