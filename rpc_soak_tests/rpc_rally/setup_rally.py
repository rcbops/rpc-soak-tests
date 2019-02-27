#!/usr/bin/python


import commands
import copy
import json
import os
import pprint
import shlex
import subprocess


def get_openrc_file():
    """
    Gets the openrc file form infra1 /root directory
    """

    print('Getting openrc file form infra1 /root/openrc')
    cmd = 'sudo ssh infra1 "cat openrc" > openrc'
    r = commands.getstatusoutput(cmd)

    # Check the return code is 0
    msg = 'Unexpected return call from {0} command. Call response: {1}'.format(cmd, r)
    assert r[0] == 0, msg

    # Check the openrc file is there
    assert os.path.exists('openrc') == True, 'openrc file not copied as expected'
    print('openrc file copied as expected to deployment VM')


def source_openrc_file():
    """
    Source openrc file and set its values as environment variables to be used
    """

    command = shlex.split("env -i bash -c 'source openrc && env'")
    proc = subprocess.Popen(command, stdout = subprocess.PIPE)

    for line in proc.stdout:
        (key, _, value) = line.partition("=")
        os.environ[key] = value

    proc.communicate()
    print('Environment variables from openrc file set')
    pprint.pprint(dict(os.environ))


def generate_rally_config():
    """
    Create the Rally JSON config file with the openrc deployment values
    """

    file_schema = {
    "openstack": {
        "auth_url": "",
        "region_name": "RegionOne",
        "endpoint_type": "internal",
        "admin": {
            "username": "admin",
            "password": "",
            "project_name": "admin",
            "project_domain_name": "Default",
            "user_domain_name": "Default"
            },
        "https_insecure": True,
        "https_cacert": ""
        }
    }

    # Getting the openrc file from infra1
    if not os.path.exists('openrc'):
        get_openrc_file()

    # Getting the openrc password and auth_url
    source_openrc_file()
    password = os.environ['OS_PASSWORD']
    auth_url = os.environ['OS_AUTH_URL']


    config_file = copy.deepcopy(file_schema)
    config_file['openstack']['admin']['password'] = password
    config_file['openstack']['auth_url'] = auth_url

    # Writting the Rally JSON config file as rally_config.json
    with open('rally_config.json', 'w') as outputfile:
        json.dump(config_file, outputfile, indent=4)

    # Showing the rally_config.json file data
    print(json.dumps(config_file, indent=4))


def delete_virtualenv(env_name):
    """
    Deletes a virtual environment (directory named env_name)
    """
    delete_cmd = 'rm -rf {0}'.format(env_name)
    delete_msg = 'Deleting Rally virtualenv. Executing: {0}'.format(delete_cmd)

    print(delete_msg)
    delete_call = commands.getstatusoutput(delete_cmd)

    print(delete_call)


def create_virtualenv(env_name=None):
    """
    Create a virtual environment for Rally named jenrally
    """
    if not env_name:
        env_name = 'jenrally'

    # Delete Rally virtualenv if it exists
    if os.path.exists(env_name):
	delete_virtualenv(env_name)

    # Create the Rally virtualenv
    create_cmd = 'virtualenv {0}'.format(env_name)
    create_msg = 'Creating Rally virtualenv. Executing: {0}'.format(create_cmd)

    print(create_msg)
    create_call = commands.getstatusoutput(create_cmd)

    print(create_call)


def install_rally(env_name='jenrally'):
    """
    Installing the rally and rally-openstack python packages at the Rally virtualenv
    Requires the Rallly virtualenv and the install_rally.py script.

    :param str env_name: Rally virtualenv directory (is required to exist)
                         The env_name jenrally is used in the install_rally.py script
    """

    # Getting the Rally virtualenv dir
    home_dir = os.getcwd()
    virtualenv_dir = '{0}/{1}'.format(home_dir, env_name)
    virtualenv_dir_msg = 'virtualenv directory at {0}'.format(virtualenv_dir)
    print(virtualenv_dir_msg)

    # Setting other file paths
    python_bin = '{0}/bin/python'.format(virtualenv_dir)
    script_file = '{0}/install_rally.py'.format(home_dir)
    activate_this_file = '{0}/bin/activate_this.py'.format(virtualenv_dir)

    # Getting into the jenrally dir
    commands.getstatusoutput('cd jenrally')

    # Activating the virtualenv and installing Rally
    execfile(activate_this_file, dict(__file__=activate_this_file))
    subprocess.call([python_bin, script_file])


if __name__=="__main__":
    generate_rally_config()
    create_virtualenv()
    install_rally()
