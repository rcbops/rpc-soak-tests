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
import os

from rpc_soak_tests.common.exceptions import InvalidTypeException

# OPENSTACK_CLOUD: value should be the cloud name in clouds.yaml
# see the clouds_example.yaml file.
# PROJECT_NAME: project name start with this value, by default is tempest*
# and this is used by utils.py methods.

DEFAULT_ENVIRONMENT_VARIABLES = ['OPENSTACK_CLOUD', 'PROJECT_NAME']


class Config(object):
    """
    Class to define environment variables used. These will define
    the attributes of the Config objects.
    """
    def __init__(self, variables=None):
        """
        :param list(str) variables: list of environment variable names.
        """

        # Defining default variables if not given.
        if not variables:
            self.variables = DEFAULT_ENVIRONMENT_VARIABLES
        else:
            data_type = type(variables)

            # Verifing that the input varables given are in a list
            if data_type != list:
                msg = 'Expecting a list instead of {0} for variables'.format(
                    data_type)
                raise InvalidTypeException(msg)
            else:
                self.variables = variables

        self.set_values()

    def set_values(self):
        for var in self.variables:
            value = os.environ.get(var)
            attr_name = var.lower()
            setattr(self, attr_name, value)
