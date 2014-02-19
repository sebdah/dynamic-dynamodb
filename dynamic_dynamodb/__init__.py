# -*- coding: utf-8 -*-
"""
Dynamic DynamoDB

Auto provisioning functionality for Amazon Web Service DynamoDB tables.


APACHE LICENSE 2.0
Copyright 2013-2014 Sebastian Dahlgren

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

from dynamic_dynamodb.core import dynamodb, gsi, table
from dynamic_dynamodb.daemon import Daemon
from dynamic_dynamodb.config_handler import CONFIGURATION as config
from dynamic_dynamodb.log_handler import LOGGER as logger


class DynamicDynamoDBDaemon(Daemon):
    """ Daemon for Dynamic DynamoDB"""

    def run(self, check_interval=1):
        """ Run the daemon

        :type check_interval: int
        :param check_interval: Delay in seconds between checks
        """
        while True:
            # Ensure provisioning
            for table_name, table_key in sorted(self.tables):
                table.ensure_provisioning(table_name, table_key)

                gsi_names = set()
                # Add regexp table names
                for gst_instance in dynamodb.table_gsis(table_name):
                    gsi_name = gst_instance[u'IndexName']
                    for gsi_key in config['tables'][table_key]['gsis'].keys():
                        if re.match(gsi_key, gsi_name):
                            logger.debug(
                                'Table {0} GSI {1} match with '
                                'GSI config key {2}'.format(
                                    table_name, gsi_name, gsi_key))
                            gsi_names.add(
                                (
                                    gsi_name,
                                    gsi_key
                                ))

                gsi_names = sorted(gsi_names)

                for gsi_name, gsi_key in gsi_names:
                    gsi.ensure_provisioning(
                        table_name,
                        table_key,
                        gsi_name,
                        gsi_key)

            # Sleep between the checks
            logger.debug('Sleeping {0} seconds until next check'.format(
                check_interval))
            time.sleep(check_interval)


def main():
    """ Main function called from dynamic-dynamodb """
    while True:
        table_names = set()
        configured_tables = config['tables'].keys()
        not_used_tables = set(configured_tables)

        # Add regexp table names
        for table_instance in dynamodb.list_tables():
            for key_name in configured_tables:
                if re.match(key_name, table_instance.table_name):
                    logger.debug("Table {0} match with config key {1}".format(
                        table_instance.table_name, key_name))
                    table_names.add(
                        (
                            table_instance.table_name,
                            key_name
                        ))
                    not_used_tables.discard(key_name)
                else:
                    logger.debug(
                        "Table {0} did not match with config key {1}".format(
                            table_instance.table_name, key_name))

        if not_used_tables:
            logger.warning(
                'No tables matching the following configured '
                'tables found: {0}'.format(
                    ', '.join(not_used_tables)))

        table_names = sorted(table_names)

        if config['global']['daemon']:
            pid_file = '/tmp/dynamic-dynamodb.{0}.pid'.format(
                config['global']['instance'])
            daemon = DynamicDynamoDBDaemon(pid_file, tables=table_names)

            if config['global']['daemon'] == 'start':
                daemon.start(
                    check_interval=config['global']['check_interval'])

            elif config['global']['daemon'] == 'stop':
                daemon.stop()
                sys.exit(0)

            elif config['global']['daemon'] == 'restart':
                daemon.restart()

            elif config['global']['daemon'] in ['foreground', 'fg']:
                daemon.run(
                    check_interval=config['global']['check_interval'])

            else:
                print 'Valid options for --daemon are start, stop and restart'
                sys.exit(1)
        else:
            # Ensure provisioning
            for table_name, table_key in table_names:
                table.ensure_provisioning(table_name, table_key)

                gsi_names = set()
                # Add regexp table names
                if 'gsis' in config['tables'][table_key]:
                    for gst_instance in dynamodb.table_gsis(table_name):
                        gsi_name = gst_instance[u'IndexName']
                        gsi_keys = config['tables'][table_key]['gsis'].keys()
                        for gsi_key in gsi_keys:
                            if re.match(gsi_key, gsi_name):
                                logger.debug(
                                    'Table {0} GSI {1} match with '
                                    'GSI config key {2}'.format(
                                        table_name, gsi_name, gsi_key))
                                gsi_names.add(
                                    (
                                        gsi_name,
                                        gsi_key
                                    ))

                gsi_names = sorted(gsi_names)

                for gsi_name, gsi_key in gsi_names:
                    gsi.ensure_provisioning(
                        table_name,
                        table_key,
                        gsi_name,
                        gsi_key)

        # Sleep between the checks
        logger.debug('Sleeping {0} seconds until next check'.format(
            config['global']['check_interval']))
        time.sleep(config['global']['check_interval'])
