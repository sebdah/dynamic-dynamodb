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

from boto.exception import JSONResponseError, BotoServerError

from dynamic_dynamodb.aws import dynamodb
from dynamic_dynamodb.core import gsi, table
from dynamic_dynamodb.daemon import Daemon
from dynamic_dynamodb.config_handler import get_global_option, get_table_option
from dynamic_dynamodb.log_handler import LOGGER as logger


class DynamicDynamoDBDaemon(Daemon):
    """ Daemon for Dynamic DynamoDB"""

    def run(self):
        """ Run the daemon

        :type check_interval: int
        :param check_interval: Delay in seconds between checks
        """
        try:
            while True:
                execute()
        except Exception as error:
            logger.exception(error)


def main():
    """ Main function called from dynamic-dynamodb """
    try:
        if get_global_option('daemon'):
            daemon = DynamicDynamoDBDaemon(
                '{0}/dynamic-dynamodb.{1}.pid'.format(
                    get_global_option('pid_file_dir'),
                    get_global_option('instance')))

            if get_global_option('daemon') == 'start':
                daemon.start()

            elif get_global_option('daemon') == 'stop':
                logger.debug('Stopping daemon')
                daemon.stop()
                logger.info('Daemon stopped')
                sys.exit(0)

            elif get_global_option('daemon') == 'restart':
                daemon.restart()

            elif get_global_option('daemon') in ['foreground', 'fg']:
                daemon.run()

            else:
                print('Valid options for --daemon are start, stop and restart')
                sys.exit(1)
        else:
            while True:
                execute()

    except Exception as error:
        logger.exception(error)


def execute():
    """ Ensure provisioning """
    boto_server_error_retries = 3

    # Ensure provisioning
    for table_name, table_key in sorted(dynamodb.get_tables_and_gsis()):
        try:
            table.ensure_provisioning(table_name, table_key)

            gsi_names = set()
            # Add regexp table names
            for gst_instance in dynamodb.table_gsis(table_name):
                gsi_name = gst_instance[u'IndexName']

                try:
                    gsi_keys = get_table_option(table_key, 'gsis').keys()

                except AttributeError:
                    # Continue if there are not GSIs configured
                    continue

                for gsi_key in gsi_keys:
                    try:
                        if re.match(gsi_key, gsi_name):
                            logger.debug(
                                'Table {0} GSI {1} matches '
                                'GSI config key {2}'.format(
                                    table_name, gsi_name, gsi_key))
                            gsi_names.add((gsi_name, gsi_key))

                    except re.error:
                        logger.error('Invalid regular expression: "{0}"'.format(
                            gsi_key))
                        sys.exit(1)

            for gsi_name, gsi_key in sorted(gsi_names):
                gsi.ensure_provisioning(
                    table_name,
                    table_key,
                    gsi_name,
                    gsi_key)

        except JSONResponseError as error:
            exception = error.body['__type'].split('#')[1]

            if exception == 'ResourceNotFoundException':
                logger.error('{0} - Table {1} does not exist anymore'.format(
                    table_name,
                    table_name))
                continue

        except BotoServerError as error:
            if boto_server_error_retries > 0:
                logger.error(
                    'Unknown boto error. Status: "{0}". Reason: "{1}"'.format(
                        error.status,
                        error.reason))
                logger.error(
                    'Please bug report if this error persists')
                boto_server_error_retries -= 1
                continue

            else:
                raise

    # Sleep between the checks
    logger.debug('Sleeping {0} seconds until next check'.format(
        get_global_option('check_interval')))
    time.sleep(get_global_option('check_interval'))
