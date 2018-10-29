#!/usr/bin/python
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

import glob
import logging
import os
import re
import subprocess
import sys
import time

"""runner.py is a script to run rally JSON scenarios that runs all
   the JSON scenarios from a directory path given, and will put the
   results (stdout) in a results directory within the directory path given
   in a timestamped .txt file.

   To run runner.py the following is expected:

    - The (rally) virutual environment is active
    - The directory path of the JSON scenario files to run is available
    - The directory path has a results directory (if not is created)
      within to store the results as timestamped .txt files.

    Use cases ex.

    $ python runner.py --tests=serial --dry-run
    $ python runner.py --tests=./nova smoke
    $ python runner.py --tests=/home/usr/rpc-soak-tests/rpc-rally/neutron
    $ python runner.py --tests='neutron' --task-args-file=args.json

    For the usage details and runner arguments see HELP below.

    References
    https://github.com/rcbops/rpc-soak-tests/tree/master/rpc-rally
    https://github.com/openstack/rally/tree/master/samples/tasks/scenarios
"""

HELP = ("""
        usage: $python runner.py --tests=<dirpath> [--dry-run][smoke]

        Run Rally tasks within the <dirpath> directory.

        required arguments:
        --tests=<dirpath> targets the Rally task to run from the
                          dirpath directory.

        optional arguments:
        --dry-run  list only the $rally task start ... cmds
        smoke      only run one rally task
        --task-args-file=<dirpath>  template variable JSON file
        """)

TASK_ARGS_FILE_PREFIX = '--task-args-file='
TESTS_PREFIX = '--tests='


def get_argv_value(args, startswith):
    """
    Gets the value of a CLI sys.argv after the = operator. For ex. it will
    return keystone for the --tests=keystone command line argument.

    :param str startswith: sys.argv starts with. For ex. --tests=
    :return: value of sys.argv param after the = operator, if the = operator
        is missing an empty string is returned.
    :rtype: str
    """
    index = [i for i, item in enumerate(args) if re.search(startswith, item)]

    if index:
        index = index.pop()
        arg = args[index]
        if '=' not in arg:
            result = ''
        else:
            result = arg.split('=')[-1]
    else:
        result = ''

    return result


def setup():
    global dry_run, test_files, file_path, log_file_path, task_args_file
    args = sys.argv[1:]

    # validating command line arguments passed to the runner
    expected_args = ['help', '--help', '-h', '--dry-run', 'smoke']
    for arg in args:
        if arg not in expected_args and not arg.startswith(
                TESTS_PREFIX) and not arg.startswith(TASK_ARGS_FILE_PREFIX):
            msg = '{0} is an invalid input argument'.format(arg)
            raise Exception(msg)

    # Displaying runner usage only if a help input argument is given
    if 'help' in args or '--help' in args or '-h' in args:
        print(HELP)
        sys.exit()

    dry_run = '--dry-run' in args

    # getting the tasks directory path from the --tests= sys.argv
    dir_path = get_argv_value(args=args, startswith=TESTS_PREFIX)
    results_path = os.path.join(dir_path, 'results')
    logs_path = os.path.join(results_path, 'logs')
    test_files = get_test_files(dir_path=dir_path)

    # getting the task args file path from the --task-args-file= sys.argv
    task_args_file = get_argv_value(args=args,
                                    startswith=TASK_ARGS_FILE_PREFIX)

    # just running one test if smoke given as a sys.argv
    if 'smoke' in args:
        test_files = test_files[0:1]

    # creating the results dir if it does not exists
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    # creating the logs dir if it does not exists
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    # setting up the results file name .txt
    file_name = time.strftime("results_%m%d_%H%M%S.txt", time.gmtime())
    file_path = os.path.join(results_path, file_name)

    # setting up logging the log file will have the same name as the results
    # file but with the .log ext and at the results/logs directory
    log_file_name = '{0}.log'.format(file_name[:-4])
    log_file_path = os.path.join(logs_path, log_file_name)
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG)

    logging.info('Set up completed')
    results_file_log = 'Results file at: {0}'.format(file_path)
    logging.info(results_file_log)

    test_files_msg = 'Running test files: {0}'.format(test_files)
    logging.info(test_files_msg)

    if dry_run:
        logging.info('Results file will NOT be created since '
                     '--dry-run param given and no tests are executed')


def welcome_msg():
    global start_secs

    start_msg = '\nWelcome to the Rally test runner! Starting Run :)\n'
    logging.info(start_msg)
    print start_msg

    start_secs = time.time()
    start_time = time.strftime("Run start %m-%d %H:%M:%S", time.gmtime(
        start_secs))

    logging.info(start_time)
    print start_time


def bye_msg():
    end_secs = time.time()
    end_time = time.strftime("Run finish %m-%d %H:%M:%S", time.gmtime(
        end_secs))
    logging.info(end_time)
    print end_time

    # calculating the load duration
    time_delta = end_secs - start_secs
    hours = time_delta // 3600
    mins = (time_delta % 3600) // 60
    secs = round(time_delta % 60, 4)

    duration_msg = '\nRun duration was {0} hours {1} mins {2} secs'.format(
        hours, mins, secs)

    if dry_run:
        dry_run_msg = '\nThis is a dry run! Results files are NOT created'
        logging.info(dry_run_msg)
        print dry_run_msg

    log_msg = 'Log file created at {0}'.format(log_file_path)
    finished_msg = '\nRun finished have a nice day!'

    logging.info(duration_msg)
    logging.info(log_msg)
    logging.info(finished_msg)

    print duration_msg
    print log_msg
    print finished_msg


def get_test_files(dir_path, file_ext='*.json'):
    file_path = os.path.join(dir_path, file_ext)
    test_files = glob.glob(file_path)
    return test_files


def run():
    rally_cmd = 'rally task start'
    results_msg = 'Results being stored at: {0}\n'.format(file_path)

    logging.info(results_msg)
    print results_msg

    for test_file in test_files:
        if task_args_file:
            # removing the = from the prefix since the rally cmd is like
            # --task-args-file args.json
            task_args = '{0} {1}'.format(TASK_ARGS_FILE_PREFIX[:-1],
                                         task_args_file)
            linux_cmd = '{0} {1} {2}'.format(rally_cmd, test_file, task_args)
        else:
            linux_cmd = '{0} {1}'.format(rally_cmd, test_file)

        run_msg = 'running: {0}'.format(linux_cmd)

        logging.info(run_msg)
        print run_msg

        if not dry_run:
            with open(file_path, 'a+') as f:
                subprocess.call(linux_cmd, shell=True, stdout=f, stderr=f)


if __name__ == "__main__":
    setup()
    welcome_msg()
    run()
    bye_msg()
