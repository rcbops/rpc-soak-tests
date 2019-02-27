#!/usr/bin/python


import commands
import os


def install_rally():
    """
    Installing the rally and rally-openstack python packages with pip
    """

    # Installing rally
    install_rally_cmd = 'pip install rally'
    install_rally_msg = 'Running: {0}'.format(install_rally_cmd)
    print(install_rally_msg)
    install_rally_call = commands.getstatusoutput(install_rally_cmd)
    print(install_rally_call)

    # Installing rally-openstack
    install_rally_openstack_cmd = 'pip install rally-openstack'
    install_rally_openstack_msg = 'Running: {0}'.format(install_rally_openstack_cmd)
    print(install_rally_openstack_msg)
    install_rally_openstack_call = commands.getstatusoutput(install_rally_openstack_cmd)
    print(install_rally_openstack_call)

    # Create the rally database if it does not exists
    create_db_cmd = 'rally db ensure'
    create_db_msg = 'Creating the Rally DB. Runninng: {0}'.format(create_db_cmd)
    print(create_db_msg)
    create_db_call = commands.getstatusoutput(create_db_cmd)
    print(create_db_call)


def run_rally(run_cmd=None):
    """
    Running Rally
    """
    home_dir = os.getcwd()
    home_dir_msg = 'At directory: {0}'.format(home_dir)
    print(home_dir_msg)

    if not run_cmd:
	run_cmd='python runner.py --tests=mnaio/serial'
    run_msg = 'Running Rally cmd: {0}'.format(run_cmd)
    print(run_msg)
    results_msg = ('Timestamped results file at {0}'
                   '/mnaio/serial/results').format(home_dir)
    run_call = commands.getstatusoutput(run_cmd)
    print(run_call)


if __name__=="__main__":
    install_rally()
    run_rally()
