RPC Openstack deployment testing 
================================


This repository contains test suites to verify
and validate the RPC-O and RPC-R OpenStack
deployments.

Te rpc_soak_test directory consists of the following,

* common: mini-wrapper framework for the OpenStack clients
* results: directory to store and share test results
* rpc_rally: testing done with OpenStack Rally
* rpc_scenarios: customized RPC tests



References
----------

Rally

* https://docs.openstack.org/developer/rally/overview/overview.html
* https://github.com/openstack/rally
* https://github.com/openstack/rally-openstack

OpenStack SDK references that may be used
for customized tests

* https://docs.openstack.org/python-openstacksdk/latest/
* https://wiki.openstack.org/wiki/OpenStackClients
* https://docs.openstack.org/mitaka/user-guide/sdk_compute_apis.html
* https://docs.openstack.org/mitaka/user-guide/sdk_neutron_apis.html
