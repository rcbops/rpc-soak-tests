#!/usr/bin/python

import glob
import os
import subprocess
import time


def welcome_msg():
    print "\nWelcome to the Rally test runner! Starting Run :)\n"
    start_time = time.strftime("Run start %m-%d %H:%M:%S", time.gmtime())
    print start_time

def bye_msg():
    end_time = time.strftime("Run finish %m-%d %H:%M:%S", time.gmtime())
    print end_time
    print '\nRun finished have a nice day!'
    
def get_test_files(file_ext='*.json'):
    test_files = glob.glob(file_ext)
    return test_files

def run():
    #dry_run = True
    dry_run = False
    test_files = get_test_files()
    #test_files = ['create-and-delete-networks.json', 'create-and-delete-subnets.json']
    file_name = time.strftime("results_%m%d_%H%M%S.txt", time.gmtime())
    file_path = os.path.join('results', file_name)
    operator = '>>'
    rally_cmd = 'rally task start'

    for test_file in test_files:
        linux_cmd = '{0} {1} {2} {3}'.format(rally_cmd, test_file, operator, file_path)
        print 'running: {0}'.format(linux_cmd)

        if not dry_run:
            subprocess.call(linux_cmd, shell=True)


if __name__=="__main__":
    welcome_msg()
    run()
    bye_msg()
