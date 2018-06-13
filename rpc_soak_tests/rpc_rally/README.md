RPC deployment testing with Rally
=================================

Rally is a benchmarking tool used for cloud verification,
benchmarking and profiling simulating user loads.

The contents of the rpc-rally directory are,

* configs: JSON file examples for registering an OpenStack deployment with Rally.
* serial: test suite with the nova, neutron, cinder and swift scenarios.

And there also test suites by OpenStack project in the following dirs,

* nova
* neutron
* cinder
* swift
* ironic
* keystone
* heat - these are still work in progress
* designate - Not available to be used at the moment since Rally is using the
python-designateclient (deprecated) that interacts with the designate
v1 API. Rally will need to be updated to use the python-openstackclient that
does interacts with the designate v2 API.

Test suites are for load testing the OpenStack deployment with Rally
and come from the Rally scenarios, see references at the end, and are in JSON.

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

*Other usefull commands  to manage deployments:*

```commandline
# to get the registered deployment list
$ rally deployment list
# to change the active deployment
$ rally deployment use --deployment <uuid or name>
```

*To see available Rally scenarios by OpenStack project:*

```rally plugin list --name ironic```

These scenarios should be available at:
https://github.com/openstack/rally/tree/master/samples/tasks/scenarios/ironic

--name is the OpenStack project, for ex. nova, neutron, etc.

Before Running Rally
--------------------

Rally runs can create tenants and users on the fly with the Admin
user or they can use pre existing tenants and users.

The Rally scenarios in the task files in this repo are configured
with the "context users" parameter to create the tenants and users
on the fly. These users will inherit the quotas from the default
class and are limited on resource creation initially.

For testing the RPC-O deployments, and avoid beeing limited
by quotas while running Rally, we increase the default
class quotas, with the Admin user and the OpenStack client,
as following:
```commandline
$openstack quota set --class --instances 200 default
$openstack quota set --class --cores 400 default
$openstack quota set --class --ram 1024000 default
$openstack quota set --class --volumes 40 default
```

These quotas should be good to run any Rally tasks/scenarios from
this repo.

Note: if the environment, where Rally testing is to be done,
is limited and can't handle these quotas, it is recommended that
a new test suite for the environment is created with Rally
tasks/scenarios with less confurrency and/or times.


Rally, for RPC-O testing, isn't running with the existing users
approach, but as a reference, here is what needs to be done in
case a test suite is desired to run with pre existing users.

- The user quotas should be increased for each user as needed by the
Rally tasks and scenarios.
- The users need to be added to the Rally deployment config file, for ex.
https://github.com/rcbops/rpc_soak_tests/blob/master/rpc_soak_tests/rpc_rally/configs/deimos01_mul.json
- The "context users" parameter needs to be removed from the Rally
tasks in a new test suite (this is what creates the tenants and users
on the fly). For ex.
https://github.com/rcbops/rpc_soak_tests/blob/master/rpc_soak_tests/rpc_rally/serial/boot-and-delete-multiple.json#L20

Running Rally
-------------

To run Rally, against the active deployment, a scenario file should
be selected, for ex.

```commandline
(rally)$ rally task start create-and-delete-networks.json
```

This ex. scenario can be found at:

https://github.com/rcbops/rpc_soak_tests/tree/master/rpc_soak_tests/rpc_rally/serial

The scenario now becomes a Rally task and its results are printed to stdout
and also an HTML, JUnit and raw JSON reports are generated and stored within
the Rally DB.


The RPC-O Rally runner
----------------------

To run multiple Rally tasks in sequence a simple runner was created and can
be seen at,

https://github.com/rcbops/rpc_soak_tests/blob/master/rpc_soak_tests/rpc_rally/runner.py

Note: its initial version can be seen within the rpc-rally/serial directory
but it has been deprecated.

This runner will pick up all the JSON task files within the same dir and
execute them as Rally tasks in sequence. The results are stored within a
results directory, for ex.

https://github.com/rcbops/rpc_soak_tests/tree/master/rpc_soak_tests/rpc_rally/serial/results

The results are timestamped text files that contain the stdout of the Rally
tasks and within the results the tasks IDs and Rally commands to generate
the HTML, JUnit or raw JSON reports can be found.

To run runner.py the following is expected:

 - The (rally) virutual environment is active
 - The direcotry path of the JSON scenario files to run is available
 - The directory path has a results directory within to store the
   results as timestamped .txt files. Still if not, It will be created.

 usage: $python runner.py --tests=`<dirpath>` [--dry-run][smoke]
 
 Run Rally tasks within the `<dirpath>` argument.
 
 required arguments:
   
   --tests=`<dirpath>` targets the Rally tasks within the dirpath directory.
 
 optional arguments:
   
   --dry-run list the $rally task start ... cmds to run (without executing)
       no results file is created.
   
   smoke only run one rally task

   --task-args-file=<dirpath>  template variable JSON file

 **Use cases ex.**

 $ python runner.py --tests=serial --dry-run
 
 $ python runner.py --tests=./nova smoke
 
 $ python runner.py --tests=/home/usr/rpc-soak-tests/rpc-rally/neutron

 **Run ex.**
```commandline
$ python runner.py --tests='neutron' --task-args-file=args.json --dry-run

Welcome to the Rally test runner! Starting Run :)

Run start 06-07 20:01:49
running: rally task start neutron/create-and-list-networks.json --task-args-file args.json >> neutron/results/results_0607_200149.txt
running: rally task start neutron/create-and-delete-networks.json --task-args-file args.json >> neutron/results/results_0607_200149.txt
running: rally task start neutron/create-and-delete-subnets.json --task-args-file args.json >> neutron/results/results_0607_200149.txt
running: rally task start neutron/create-and-delete-ports.json --task-args-file args.json >> neutron/results/results_0607_200149.txt
Run finish 06-07 20:01:49

This is a dry run! Results files are NOT created

Run duration was 0.0 hours 0.0 mins 0.0002 secs
Log file created at neutron/results/logs/results_0607_200149.log

Run finished have a nice day!
```

The Rally Tempest Verifier
--------------------------

Rally can run tempest tests with its verification component known as
"rally verify". With this component you can create tempest verifiers for
the Rally OpenStack registered deployments as shown in the example below.

**To create the verifier**
```commandline
$ rally verify create-verifier --type tempest --name tempver-eureka-queens --version 17.2.0
2018-06-05 20:39:12.885 33527 INFO rally.api [-] Creating verifier 'tempver-eureka-queens'.
2018-06-05 20:39:12.936 33527 INFO rally.verification.manager [-] Cloning verifier repo from https://git.openstack.org/openstack/tempest.
2018-06-05 20:39:19.219 33527 INFO rally.verification.manager [-] Switching verifier repo to the '17.2.0' version.
2018-06-05 20:39:19.344 33527 INFO rally.verification.manager [-] Creating virtual environment. It may take a few minutes.
2018-06-05 20:39:34.179 33527 INFO rally.api [-] Verifier 'tempver-eureka-queens' (UUID=5bfb7d25-ead7-45d8-a038-85a49bfe5412) has been successfully created!
Using verifier 'tempver-eureka-queens' (UUID=5bfb7d25-ead7-45d8-a038-85a49bfe5412) as the default verifier for the future CLI operations.
```
Note: the verifier created is for the active Rally deployment. The --version
parameter is optional but in this case the tempest version 17.2.0 is used
since there seems to be an issue when using a rally version below 0.11.
Also, a --source param can be used to point to a local installation of
tempest or an alternate git repository, for ex. /home/ubuntu/tempest/ or
https://github.com/openstack/tempest.git


**To configure the verifier**

```commandline
$ rally verify configure-verifier
2018-06-05 20:56:35.756 33611 INFO rally.api [-] Configuring verifier 'tempver-eureka-queens' (UUID=5bfb7d25-ead7-45d8-a038-85a49bfe5412) for deployment 'eureka_queens' (UUID=9645acaa-d81e-48ac-8b77-9fe1d18f70f5).
2018-06-05 20:56:36.593 33611 INFO rally.api [-] Verifier 'tempver-eureka-queens' (UUID=5bfb7d25-ead7-45d8-a038-85a49bfe5412) has been successfully configured for deployment 'eureka_queens' (UUID=9645acaa-d81e-48ac-8b77-9fe1d18f70f5)!
```
Note: the --show argument can be used to see the tempest config file that will
be stored at the .rally verification dir, for ex.
```commandline
.rally/verification/verifier-5bfb7d25-ead7-45d8-a038-85a49bfe5412/for-deployment-9645acaa-d81e-48ac-8b77-9fe1d18f70f5
```

**Starting a verification**

To run all tempest tests
```commandline
$ rally verify start
```

To run tests by product
```commandline
$ rally verify start --pattern set=compute
```

Note: available sets are full, smoke, compute, identity, image, network,
object_storage, volume and scenario. The number of test suites
depends on the Tempest version used.

To run a certain set of tests from a test class or a single test, for ex.
```commandline
$ rally verify start --pattern tempest.api.compute.servers.test_create_server.ServersTestJSON
$ rally verify start --pattern tempest.api.network.test_networks.NetworksTest --detailed
$ rally verify start --regex tempest.api.compute.admin.test_flavors.FlavorsAdminTestJSON.test_create_flavor_using_string_ram
```

Note: the --detailed argument can be used to see the errors of failed tests after the verification finishes

**Other useful commands**
```commandline
$ rally verify list-verifiers
$ rally verify delete-verifier --id <UUID>
```
To configure the verifier vs another Rally deployment
```commandline
$ rally verify configure-verifier --deployment-id <UUID or name of a deployment>
```

To run a verifier given by ID vs a Rally deployment given by ID too
```commandline
$ rally verify start --id <UUID or name of a verifier> --deployment-id <UUID or name of a deployment>
```

To rerun failed tests
```commandline
$ rally verify rerun --uuid <UUID of a verification> --failed
```
Note: --failed is optional and can be used to rerun only failed tests of a
verification. If not given all tests of the verification will rerun.

To see detailed information of a verification
```commandline
$ rally verify show <UUID of a verification>
```

To generate a report of a verification
```commandline
$ rally verify report <UUID of a verification>
```

To just list the tests to run, for ex.
```commandline
$ rally verify list-verifier-tests --pattern set=scenario
```

References
----------

Rally Quick Start

https://docs.openstack.org/developer/rally/quick_start/index.html

Rally scenarios

https://github.com/openstack/rally/tree/master/samples/tasks/scenarios

Rally Tempest Verifier

https://docs.openstack.org/developer/rally/quick_start/tutorial/step_10_verifying_cloud_via_tempest_verifier.html

Rally Verify CLI reference

https://docs.openstack.org/rally/latest/verification/cli_reference.html

Tempest API tests

https://github.com/openstack/tempest/tree/master/tempest/api

Tempest Scenario tests

https://github.com/openstack/tempest/tree/master/tempest/scenario