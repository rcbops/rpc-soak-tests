#!/usr/bin/python

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
    - The direcotry path of the JSON scenario files to run is available
    - The directory path has a results directory within to store the
      results as timestamped .txt files. It will be created if it doesn't
      exists.

    usage: python runner.py --tests=<dirpath> [--dry-run][smoke]

    # dirpath is where the JSON scenario files and the results dir is.
    # --dry-run is only to list the rally tasks to run (without running)
    # smoke is to only run one test

    Use cases ex.

    # keystone in this example is a subdirectory where the runner.py
    # is located. Still it can also be a relative or absolute path.

    $ python runner.py --tests=keystone
    $ python runner.py --tests=./keystone/create-and-list-tenants.json
    $ python runner.py --tests=/home/usr/rpc-soak-tests/rpc-rally/keystone

    References
    https://github.com/rcbops/rpc-soak-tests/tree/master/rpc-rally
    https://github.com/openstack/rally/tree/master/samples/tasks/scenarios

"""

def setup():

    global dry_run, test_files, file_path

    args = sys.argv
    dry_run = '--dry-run' in args

    # sys.argv --tests=keystone for ex. getting the keystone dir
    tests_index = [i for i, item in enumerate(args) if re.search('--tests=', item)].pop()
    tests_param = args[tests_index]
    dir_path = tests_param.split('=')[-1]
    results_path = os.path.join(dir_path, 'results')
    logs_path = os.path.join(results_path, 'logs')
    test_files = get_test_files(dir_path=dir_path)

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

    # setting up logging the log file will have the same name as the results file but
    # with .log (instead of .txt) and will be at the results/logs directory
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
    start_time = time.strftime("Run start %m-%d %H:%M:%S", time.gmtime(start_secs))

    logging.info(start_time)
    print start_time
    
def bye_msg():
    end_secs = time.time()
    end_time = time.strftime("Run finish %m-%d %H:%M:%S", time.gmtime(end_secs))
    logging.info(end_time)
    print end_time

    # calculating the load duration
    time_delta = end_secs - start_secs
    hours = time_delta // 3600
    mins = (time_delta % 3600) // 60
    secs = round(time_delta % 60, 4)

    duration_msg = '\nRun duration was {0} hours {1} mins {2} secs'.format(hours, mins, secs)
    finished_msg = '\nRun finished have a nice day!'
    logging.info(duration_msg)
    logging.info(finished_msg)
    print duration_msg
    print finished_msg

def get_test_files(dir_path, file_ext='*.json'):
    file_path = os.path.join(dir_path, file_ext)
    test_files = glob.glob(file_path)
    return test_files

def run():
    operator = '>>'
    rally_cmd = 'rally task start'

    for test_file in test_files:
        linux_cmd = '{0} {1} {2} {3}'.format(rally_cmd, test_file, operator, file_path)
        run_msg = 'running: {0}'.format(linux_cmd)

        logging.info(run_msg)
        print run_msg

        if not dry_run:
            subprocess.call(linux_cmd, shell=True)


if __name__=="__main__":
    setup()
    welcome_msg()
    run()
    bye_msg()
