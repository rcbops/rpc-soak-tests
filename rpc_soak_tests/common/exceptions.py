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


class SoakTestException(Exception):
    message = 'Not Set'

    def __init__(self, message=None):
        self.message = message or self.message

    def __str__(self):
        return str(self.message)


class InvalidTypeException(SoakTestException):
    message = 'Invalid data type exception'


class UnableToDeleteResource(SoakTestException):
    message = 'Unable to delete resource'


class MissingDeleteParams(SoakTestException):
    message = 'Project IDs or resources names missing'
