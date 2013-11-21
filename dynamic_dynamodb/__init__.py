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
import re
import sys
import time

import dynamic_dynamodb.core as core
from dynamic_dynamodb.daemon import Daemon
from dynamic_dynamodb.config_handler import CONFIGURATION as configuration
from dynamic_dynamodb.log_handler import LOGGER as logger


class DynamicDynamoDBDaemon(Daemon):
    """ Daemon for Dynamic DynamoDB"""

    def run(self, check_interval=1):
        """ Run the daemon

        :type check_interval: int
        :param check_interval: Delay in seconds between checks
        """
        while True:
            used_keys = set()
            table_names = set()
            configured_tables = configuration['tables'].keys()

            # Add regexp table names
            for table_name in core.dynamodb.list_tables():
                for key_name in configured_tables:
                    if re.match(key_name, table_name):
                        logger.debug(
                            "Table {0} match with config key {1}".format(
                                table_name, key_name))
                        table_names.add((table_name, key_name))
                        used_keys.add(key_name)

            # Remove used tables
            for table_name in used_keys:
                configured_tables.remove(table_name)

            # Ensure provisioning
            for table_name, key_name in sorted(table_names):
                core.ensure_provisioning(table_name, key_name)

            # Sleep between the checks
            time.sleep(check_interval)


def main():
    """ Main function called from dynamic-dynamodb """
    if configuration['global']['daemon']:
        pid_file = '/tmp/dynamic-dynamodb.{0}.pid'.format(
            configuration['global']['instance'])
        daemon = DynamicDynamoDBDaemon(pid_file)

        if configuration['global']['daemon'] == 'start':
            daemon.start(
                check_interval=configuration['global']['check_interval'])

        elif configuration['global']['daemon'] == 'stop':
            daemon.stop()

        elif configuration['global']['daemon'] == 'restart':
            daemon.restart()

        elif configuration['global']['daemon'] in ['foreground', 'fg']:
            daemon.run(
                check_interval=configuration['global']['check_interval'])

        else:
            print 'Valid options for --daemon are start, stop and restart'
            sys.exit(1)
    else:
        table_names = set()
        used_keys = set()
        configured_tables = configuration['tables'].keys()

        # Add regexp table names
        for table_name in core.dynamodb.list_tables():
            for key_name in configured_tables:
                if re.match(key_name, table_name):
                    logger.debug("Table {0} match with config key {1}".format(
                        table_name, key_name))
                    table_names.add((table_name, key_name))
                    used_keys.add(key_name)

        # Remove used tables
        for table_name in used_keys:
            configured_tables.remove(table_name)

        # Ensure provisioning
        for table_name, key_name in sorted(table_names):
            core.ensure_provisioning(table_name, key_name)
