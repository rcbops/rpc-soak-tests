RPC deployment testing with Rally
=================================

Rally is a benchmarking tool used for cloud verification,
benchmarking and profiling simulating user loads.

The contents of the rpc-rally directory are,

* configs: examples of how to register a Rally deployment.
* serial: test suite for the RPC OpenStack deployment
validation and verification. These tests come from the
Rally scenarios (see References) and are in JSON.

Rally uses two types of JSON files, the ones that
Register the OpenStack deployment, described below
and examples in the config directory, 
and the ones used for running Rally against the 
deployment "the Rally scenarios". 
If more scenarios are desired, that doesn't
exist within the Rally repository, then Rally development
is to be done.


Installing Rally
----------------

*Installing pre-dependencies, Ubuntu ex.*
```commandline
$sudo apt-get install git python-pip
$sudo apt-get install libffi-dev libpq-dev libssl-dev libxml2-dev libxslt1-dev
```

*Installing Rally*
```commandline
$wget -q -O- https://raw.githubusercontent.com/openstack/rally/master/install_rally.sh | bash
# or using curl:
$curl https://raw.githubusercontent.com/openstack/rally/master/install_rally.sh | bash
# or getting the install script with curl
$curl https://raw.githubusercontent.com/openstack/rally/master/install_rally.sh >> install_rally.sh
```

**Note: Rally requires Python 2.7 or 3.4**

If installed as root Rally will be installed system wide,
if installed as a regullar user it will be installed in the
user home directory creating the rally virtualenv there,
for ex. ~/rally/

This environment should be activated to use Rally.
```commandline
$cd rally
$. bin/activate
(rally)$
```
**Note: running Rally commands require the environment to
be active.**

Rally also creates in the user home directory the .rally dir.
This directory contains the registered OpenStack deployments
and a symlink "openrc" that points to the active deployment
in use.

Registering the OpenStack deployment
------------------------------------
With rally installed the OpenStack deployment to be tested
can be registered as a rally deployment with its openrc
file or data to be used. This can be done by two different
ways as shown below.

*From environment variables set by openrc*
```commandline
(rally)$rally deployment create --fromenv --name=<deploymentName>

#openrc file ex.
$ cat openrc
export OS_AUTH_URL='http://172.21.8.156:5000/v3/'
export OS_USERNAME='rally_admin'
export OS_PASSWORD='secret01'
export OS_TENANT_NAME='rally_testing'
export OS_PROJECT_NAME='rally_testing'
export OS_REGION_NAME='RegionOne'
export OS_ENDPOINT_TYPE='adminURL'
export OS_INTERFACE='admin'
export OS_IDENTITY_API_VERSION=3
export OS_USER_DOMAIN_NAME='Default'
export OS_PROJECT_DOMAIN_NAME='Default'

```

*From a JSON configuration file with data from openrc*
```commandline
(rally)$rally deployment create --file=<fileName>.json --name=<deploymentName>

#JSON config file ex.
$ cat deimos02_mul.json
{
    "openstack": {
        "auth_url": "http://172.21.8.156:5000/v3/",
        "region_name": "RegionOne",
        "endpoint_type": "admin",
        "admin": {
            "username": "rally_admin",
            "password": "secret01",
            "project_name": "rally_testing",
            "project_domain_name": "Default",
            "user_domain_name": "Default"
        },
        "https_insecure": True,
        "https_cacert": ""
    }
}
```

Checking the registered deployment
----------------------------------
After registering the deployment is good to check it
to make sure Rally is able to interact with it. This is
done just like the following ex.

```commandline
(rally)$ rally deployment check
--------------------------------------------------------------------------------
Platform openstack:
--------------------------------------------------------------------------------

Available services:
+-------------+----------------+-----------+
| Service     | Service Type   | Status    |
+-------------+----------------+-----------+
| __unknown__ | load-balancer  | Available |
| __unknown__ | placement      | Available |
| __unknown__ | volumev2       | Available |
| __unknown__ | volumev3       | Available |
| cinder      | volume         | Available |
| cloud       | cloudformation | Available |
| glance      | image          | Available |
| heat        | orchestration  | Available |
| keystone    | identity       | Available |
| neutron     | network        | Available |
| nova        | compute        | Available |
+-------------+----------------+-----------+
```

This deployment is now registered in the .rally dir and
the "openrc" file points to it making it the active
deployment to be used.

*Other usefull commands  to manage deployments are:*

```commandline
# to get the registered deployment list
$ rally deployment list
# to change the active deployment
$ rally deployment use --deployment <uuid or name>
```

Running Rally
-------------

To run Rally, against the active deployment, a scenario file should
be selected, for ex.

```commandline
(rally)$ rally task start create-and-delete-networks.json
```

This ex. scenario can be found at:

https://github.com/rcbops/rpc-soak-tests/tree/master/rpc-rally/serial

The scenario now becomes a Rally task and its results are printed to stdout
and also an HTML, JUnit and raw JSON reports are generated and stored within
the Rally DB.

To run multiple scenarios in sequence a simple runner was created and can
be seen at,

https://github.com/rcbops/rpc-soak-tests/blob/master/rpc-rally/serial/runner.py

This runner will pick up all the JSON scenario files within the same dir and
execute them as Rally tasks in sequence. The results are stored within a
results directory, for ex.

https://github.com/rcbops/rpc-soak-tests/tree/master/rpc-rally/serial/results

And are timestamped text files that contain the stdout of the Rally tasks
and within are the tasks IDs and Rally commands to generate the HTML, JUnit
and or raw JSON reports if desired. Examples of these files can be seen
within the results directory mentioned above.

**Note: the runner is still work in progress but fully functional.**


References
----------

Rally Quick Start

https://docs.openstack.org/developer/rally/quick_start/index.html

Rally scenarios

https://github.com/openstack/rally/tree/master/samples/tasks/scenarios
