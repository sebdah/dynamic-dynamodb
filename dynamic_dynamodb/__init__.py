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
import json
import re
import sys
import time
import threading
import dynamic_dynamodb.log_handler as log_handler

from boto.exception import JSONResponseError, BotoServerError

from dynamic_dynamodb.aws import dynamodb
from dynamic_dynamodb.core import gsi, table
from dynamic_dynamodb.daemon import Daemon
from dynamic_dynamodb.config_handler import get_global_option, get_table_option
from dynamic_dynamodb.log_handler import LOGGER as logger

CHECK_STATUS = {
    'tables': {},
    'gsis': {}
}

table_threads = {}
stop_thread = False

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
        if get_global_option('show_config'):
            print json.dumps(config.get_configuration(), indent=2)
        elif get_global_option('daemon'):
            daemon = DynamicDynamoDBDaemon(
                '{0}/dynamic-dynamodb.{1}.pid'.format(
                    get_global_option('pid_file_dir'),
                    get_global_option('instance')))

            if get_global_option('daemon') == 'start':
                logger.debug('Starting daemon')
                try:
                    daemon.start()
                    logger.info('Daemon started')
                except IOError as error:
                    logger.error('Could not create pid file: {0}'.format(error))
                    logger.error('Daemon not started')
            elif get_global_option('daemon') == 'stop':
                logger.debug('Stopping daemon')
                daemon.stop()
                logger.info('Daemon stopped')
                sys.exit(0)

            elif get_global_option('daemon') == 'restart':
                logger.debug('Restarting daemon')
                daemon.restart()
                logger.info('Daemon restarted')

            elif get_global_option('daemon') in ['foreground', 'fg']:
                logger.debug('Starting daemon in foreground')
                daemon.run()
                logger.info('Daemon started in foreground')

            else:
                print(
                    'Valid options for --daemon are start, '
                    'stop, restart, and foreground')
                sys.exit(1)
        else:
            if get_global_option('run_once'):
                execute()
            else:
                while True:
                    execute()

    except Exception as error:
        logger.exception(error)
    except KeyboardInterrupt:
        while threading.active_count() > 1:
            for thread in table_threads.values():
                thread.do_run = False
            logger.info('Waiting for all threads... {}s'.format(get_global_option('check_interval')))
            time.sleep(get_global_option('check_interval'))
        raise

def execute_table(table_name, table_key, table_logger):
    try:
        table_num_consec_read_checks = \
            CHECK_STATUS['tables'][table_name]['reads']
    except KeyError:
        table_num_consec_read_checks = 0

    try:
        table_num_consec_write_checks = \
            CHECK_STATUS['tables'][table_name]['writes']
    except KeyError:
        table_num_consec_write_checks = 0

    try:
        # The return var shows how many times the scale-down criteria
        #  has been met. This is coupled with a var in config,
        # "num_intervals_scale_down", to delay the scale-down
        table_num_consec_read_checks, table_num_consec_write_checks = \
            table.ensure_provisioning(
                table_name,
                table_key,
                table_num_consec_read_checks,
                table_num_consec_write_checks,
                table_logger)

        CHECK_STATUS['tables'][table_name] = {
            'reads': table_num_consec_read_checks,
            'writes': table_num_consec_write_checks
        }

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
                        table_logger.debug(
                            'Table {0} GSI {1} matches '
                            'GSI config key {2}'.format(
                                table_name, gsi_name, gsi_key))
                        gsi_names.add((gsi_name, gsi_key))

                except re.error:
                    table_logger.error('Invalid regular expression: "{0}"'.format(
                        gsi_key))
                    sys.exit(1)

        for gsi_name, gsi_key in sorted(gsi_names):
            try:
                gsi_num_consec_read_checks = \
                    CHECK_STATUS['gsis'][gsi_name]['reads']
            except KeyError:
                gsi_num_consec_read_checks = 0

            try:
                gsi_num_consec_write_checks = \
                    CHECK_STATUS['gsis'][gsi_name]['writes']
            except KeyError:
                gsi_num_consec_write_checks = 0

            gsi_num_consec_read_checks, gsi_num_consec_write_checks = \
                gsi.ensure_provisioning(
                    table_name,
                    table_key,
                    gsi_name,
                    gsi_key,
                    gsi_num_consec_read_checks,
                    gsi_num_consec_write_checks,
                    table_logger)

            CHECK_STATUS['gsis'][gsi_name] = {
                'reads': gsi_num_consec_read_checks,
                'writes': gsi_num_consec_write_checks
            }

    except JSONResponseError as error:
        exception = error.body['__type'].split('#')[1]

        if exception == 'ResourceNotFoundException':
            table_logger.error('{0} - Table {1} does not exist anymore'.format(
                table_name,
                table_name))

    except BotoServerError as error:
        if boto_server_error_retries > 0:
            table_logger.error(
                'Unknown boto error. Status: "{0}". '
                'Reason: "{1}". Message: {2}'.format(
                    error.status,
                    error.reason,
                    error.message))
            table_logger.error(
                'Please bug report if this error persists')
            boto_server_error_retries -= 1
        else:
            raise

def execute_table_in_loop(table_name, table_key, table_logger):
    if not get_global_option('daemon') and get_global_option('run_once'):
        execute_table(table_name, table_key)
    else:
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            execute_table(table_name, table_key, table_logger)
            logger.debug('Sleeping {0} seconds until next check'.format(
                get_global_option('check_interval')))
            time.sleep(get_global_option('check_interval'))
            
  
def execute_in_thread(table_name, table_key):
    if table_name in table_threads:
        thread = table_threads.get(table_name)
        if thread.isAlive():
            logger.debug("Thread {} still running".format(table_name))
        else:
            logger.error("Thread {} was stopped!".format(table_name))
            sys.exit(1)
    else:
        table_logger=log_handler.getTableLogger(table_name)
        logger.info("Start new thread: " + table_name)
        thread = threading.Thread(target=execute_table_in_loop, args=[table_name, table_key, table_logger])
        table_threads[table_name]=thread
        thread.start()

def execute():
    """ Ensure provisioning """
    boto_server_error_retries = 3

    # Ensure provisioning
    for table_name, table_key in sorted(dynamodb.get_tables_and_gsis()):
        logger.debug("Table: " + table_name)
        execute_in_thread(table_name, table_key)
    # Sleep between the checks
    if not get_global_option('run_once'):
        logger.debug('Sleeping {0} seconds until next thread check'.format(60))
        time.sleep(60)
