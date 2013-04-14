# -*- coding: utf-8 -*-
"""
Dynamic DynamoDB

Auto provisioning functionality for Amazon Web Service DynamoDB tables.


APACHE LICENSE 2.0
Copyright 2013 Sebastian Dahlgren

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
import sys
import time

import core
from daemon import Daemon
from config_handler import CONFIGURATION as configuration

VERSION = '1.0.0'


class DynamicDynamoDBDaemon(Daemon):
    """ Daemon for Dynamic DynamoDB"""

    def run(self, check_interval=1):
        """ Run the daemon

        :type check_interval: int
        :param check_interval: Delay in seconds between checks
        """
        while True:
            core.ensure_provisioning(configuration['table_name'])
            time.sleep(check_interval)


def main():
    """ Main function called from dynamic-dynamodb """
    if configuration['daemon']:
        daemon = DynamicDynamoDBDaemon('/tmp/daemon.pid')
        if configuration['daemon'] == 'start':
            daemon.start(check_interval=configuration['check_interval'])
        elif configuration['daemon'] == 'stop':
            daemon.stop()
        elif configuration['daemon'] == 'restart':
            daemon.restart()
        else:
            print 'Valid options for --daemon are start, stop and restart'
            sys.exit(1)
    else:
        core.ensure_provisioning(configuration['table_name'])


def version():
    """ Returns the version number """
    return VERSION

