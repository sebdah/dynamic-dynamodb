# -*- coding: utf-8 -*-
""" Handle most tasks related to DynamoDB interaction """
import re
import sys
import time
import datetime

from boto import dynamodb2
from boto.dynamodb2.table import Table
from boto.exception import DynamoDBResponseError, JSONResponseError

from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import (
    get_configured_tables,
    get_global_option,
    get_gsi_option,
    get_table_option)
from dynamic_dynamodb.aws import sns


def get_tables_and_gsis():
    """ Get a set of tables and gsis and their configuration keys

    :returns: set -- A set of tuples (table_name, table_conf_key)
    """
    table_names = set()
    configured_tables = get_configured_tables()
    not_used_tables = set(configured_tables)

    # Add regexp table names
    for table_instance in list_tables():
        for key_name in configured_tables:
            try:
                if re.match(key_name, table_instance.table_name):
                    logger.debug("Table {0} match with config key {1}".format(
                        table_instance.table_name, key_name))

                    # Notify users about regexps that match multiple tables
                    if table_instance.table_name in [x[0] for x in table_names]:
                        logger.warning(
                            'Table {0} matches more than one regexp in config, '
                            'skipping this match: "{1}"'.format(
                                table_instance.table_name, key_name))
                    else:
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
            except re.error:
                logger.error('Invalid regular expression: "{0}"'.format(
                    key_name))
                sys.exit(1)

    if not_used_tables:
        logger.warning(
            'No tables matching the following configured '
            'tables found: {0}'.format(', '.join(not_used_tables)))

    return sorted(table_names)


def get_table(table_name):
    """ Return the DynamoDB table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: boto.dynamodb.table.Table
    """
    try:
        table = Table(table_name, connection=DYNAMODB_CONNECTION)
    except DynamoDBResponseError as error:
        dynamodb_error = error.body['__type'].rsplit('#', 1)[1]
        if dynamodb_error == 'ResourceNotFoundException':
            logger.error(
                '{0} - Table {1} not found'.format(table_name, table_name))

        raise

    return table


def get_gsi_status(table_name, gsi_name):
    """ Return the DynamoDB table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :returns: str
    """
    try:
        desc = DYNAMODB_CONNECTION.describe_table(table_name)
    except JSONResponseError:
        raise

    for gsi in desc[u'Table'][u'GlobalSecondaryIndexes']:
        if gsi[u'IndexName'] == gsi_name:
            return gsi[u'IndexStatus']


def get_provisioned_gsi_read_units(table_name, gsi_name):
    """ Returns the number of provisioned read units for the table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :returns: int -- Number of read units
    """
    try:
        desc = DYNAMODB_CONNECTION.describe_table(table_name)
    except JSONResponseError:
        raise

    for gsi in desc[u'Table'][u'GlobalSecondaryIndexes']:
        if gsi[u'IndexName'] == gsi_name:
            read_units = int(
                gsi[u'ProvisionedThroughput'][u'ReadCapacityUnits'])
            break

    logger.debug(
        '{0} - GSI: {1} - Currently provisioned read units: {2:d}'.format(
            table_name, gsi_name, read_units))
    return read_units


def get_provisioned_gsi_write_units(table_name, gsi_name):
    """ Returns the number of provisioned write units for the table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :returns: int -- Number of write units
    """
    try:
        desc = DYNAMODB_CONNECTION.describe_table(table_name)
    except JSONResponseError:
        raise

    for gsi in desc[u'Table'][u'GlobalSecondaryIndexes']:
        if gsi[u'IndexName'] == gsi_name:
            write_units = int(
                gsi[u'ProvisionedThroughput'][u'WriteCapacityUnits'])
            break

    logger.debug(
        '{0} - GSI: {1} - Currently provisioned write units: {2:d}'.format(
            table_name, gsi_name, write_units))
    return write_units


def get_provisioned_table_read_units(table_name):
    """ Returns the number of provisioned read units for the table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: int -- Number of read units
    """
    try:
        desc = DYNAMODB_CONNECTION.describe_table(table_name)
    except JSONResponseError:
        raise

    read_units = int(
        desc[u'Table'][u'ProvisionedThroughput'][u'ReadCapacityUnits'])

    logger.debug('{0} - Currently provisioned read units: {1:d}'.format(
        table_name, read_units))
    return read_units


def get_provisioned_table_write_units(table_name):
    """ Returns the number of provisioned write units for the table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: int -- Number of write units
    """
    try:
        desc = DYNAMODB_CONNECTION.describe_table(table_name)
    except JSONResponseError:
        raise

    write_units = int(
        desc[u'Table'][u'ProvisionedThroughput'][u'WriteCapacityUnits'])

    logger.debug('{0} - Currently provisioned write units: {1:d}'.format(
        table_name, write_units))
    return write_units


def get_table_status(table_name):
    """ Return the DynamoDB table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: str
    """
    try:
        desc = DYNAMODB_CONNECTION.describe_table(table_name)
    except JSONResponseError:
        raise

    return desc[u'Table'][u'TableStatus']


def list_tables():
    """ Return list of DynamoDB tables available from AWS

    :returns: list -- List of DynamoDB tables
    """
    tables = []

    try:
        table_list = DYNAMODB_CONNECTION.list_tables()
        while True:
            for table_name in table_list[u'TableNames']:
                tables.append(get_table(table_name))

            if u'LastEvaluatedTableName' in table_list:
                table_list = DYNAMODB_CONNECTION.list_tables(
                    table_list[u'LastEvaluatedTableName'])
            else:
                break

    except DynamoDBResponseError as error:
        dynamodb_error = error.body['__type'].rsplit('#', 1)[1]

        if dynamodb_error == 'ResourceNotFoundException':
            logger.error('No tables found')
        elif dynamodb_error == 'AccessDeniedException':
            logger.debug(
                'Your AWS API keys lack access to listing tables. '
                'That is an issue if you are trying to use regular '
                'expressions in your table configuration.')
        elif dynamodb_error == 'UnrecognizedClientException':
            logger.error(
                'Invalid security token. Are your AWS API keys correct?')
        else:
            logger.error(
                (
                    'Unhandled exception: {0}: {1}. '
                    'Please file a bug report at '
                    'https://github.com/sebdah/dynamic-dynamodb/issues'
                ).format(
                    dynamodb_error,
                    error.body['message']))

    except JSONResponseError as error:
        logger.error('Communication error: {0}'.format(error))
        sys.exit(1)

    return tables


def update_table_provisioning(
        table_name, key_name, reads, writes, retry_with_only_increase=False):
    """ Update provisioning for a given table

    :type table_name: str
    :param table_name: Name of the table
    :type key_name: str
    :param key_name: Configuration option key name
    :type reads: int
    :param reads: New number of provisioned read units
    :type writes: int
    :param writes: New number of provisioned write units
    :type retry_with_only_increase: bool
    :param retry_with_only_increase: Set to True to ensure only increases
    """
    table = get_table(table_name)
    current_reads = int(get_provisioned_table_read_units(table_name))
    current_writes = int(get_provisioned_table_write_units(table_name))

    if retry_with_only_increase:
        # Ensure that we are only doing increases
        if current_reads > reads:
            reads = current_reads
        if current_writes > writes:
            writes = current_writes

        # Return if we do not need to scale at all
        if reads == current_reads and writes == current_writes:
            logger.info(
                '{0} - No need to scale up reads nor writes'.format(
                    table_name))
            return

        logger.info(
            '{0} - Retrying to update provisioning, excluding any decreases. '
            'Setting new reads to {1} and new writes to {2}'.format(
                table_name, reads, writes))

    # Check that we are in the right time frame
    maintenance_windows = get_table_option(key_name, 'maintenance_windows')
    if maintenance_windows:
        if not __is_table_maintenance_window(table_name, maintenance_windows):
            logger.warning(
                '{0} - We are outside a maintenace window. '
                'Will only perform up scaling activites'.format(table_name))

            # Ensure that we are only doing increases
            if current_reads > reads:
                reads = current_reads
            if current_writes > writes:
                writes = current_writes

            # Return if we do not need to scale up
            if reads == current_reads and writes == current_writes:
                logger.info(
                    '{0} - No need to scale up reads nor writes'.format(
                        table_name))
                return

        else:
            logger.info(
                '{0} - Current time is within maintenance window'.format(
                    table_name))

    logger.info(
        '{0} - Updating provisioning to {1} reads and {2} writes'.format(
            table_name, reads, writes))

    # Return if dry-run
    if get_global_option('dry_run'):
        return

    try:
        table.update(
            throughput={
                'read': reads,
                'write': writes
            })

        # See if we should send notifications for scale-down, scale-up or both
        sns_message_types = []
        if current_reads > reads or current_writes > writes:
            sns_message_types.append('scale-down')
        if current_reads < reads or current_writes < writes:
            sns_message_types.append('scale-up')

        message = []
        if current_reads > reads:
            message.append('{0} - Reads: DOWN from {1} to {2}\n'.format(
                table_name, current_reads, reads))
        elif current_reads < reads:
            message.append('{0} - Reads: UP from {1} to {2}\n'.format(
                table_name, current_reads, reads))
        if current_writes > writes:
            message.append('{0} - Writes: DOWN from {1} to {2}\n'.format(
                table_name, current_writes, writes))
        elif current_writes < writes:
            message.append('{0} - Writes: UP from {1} to {2}\n'.format(
                table_name, current_writes, writes))

        sns.publish_table_notification(
            key_name,
            ''.join(message),
            sns_message_types,
            subject='Updated provisioning for table {0}'.format(table_name))
    except JSONResponseError as error:
        exception = error.body['__type'].split('#')[1]
        know_exceptions = [
            'LimitExceededException',
            'ValidationException',
            'ResourceInUseException']

        if exception in know_exceptions:
            logger.warning('{0} - {1}: {2}'.format(
                table_name, exception, error.body['message']))
        else:
            if 'message' in error.body:
                msg = error.body['message']
            else:
                msg = error

            logger.error(
                (
                    '{0} - Unhandled exception: {1}: {2}. '
                    'Please file a bug report at '
                    'https://github.com/sebdah/dynamic-dynamodb/issues'
                ).format(table_name, exception, msg))

        if (not retry_with_only_increase and
                exception == 'LimitExceededException'):
            logger.info(
                '{0} - Will retry to update provisioning '
                'with only increases'.format(table_name))
            update_table_provisioning(
                table_name,
                key_name,
                reads,
                writes,
                retry_with_only_increase=True)


def update_gsi_provisioning(
        table_name, table_key, gsi_name, gsi_key,
        reads, writes, retry_with_only_increase=False):
    """ Update provisioning on a global secondary index

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type gsi_key: str
    :param gsi_key: GSI configuration option key name
    :type reads: int
    :param reads: Number of reads to provision
    :type writes: int
    :param writes: Number of writes to provision
    :type retry_with_only_increase: bool
    :param retry_with_only_increase: Set to True to ensure only increases
    """
    current_reads = int(get_provisioned_gsi_read_units(table_name, gsi_name))
    current_writes = int(get_provisioned_gsi_write_units(table_name, gsi_name))

    if retry_with_only_increase:
        # Ensure that we are only doing increases
        if current_reads > reads:
            reads = current_reads
        if current_writes > writes:
            writes = current_writes

        # Return if we do not need to scale at all
        if reads == current_reads and writes == current_writes:
            logger.info(
                '{0} - GSI: {1} - No need to scale up reads nor writes'.format(
                    table_name, gsi_name))
            return

        logger.info(
            '{0} - GSI: {1} - Retrying to update provisioning, '
            'excluding any decreases. '
            'Setting new reads to {2} and new writes to {3}'.format(
                table_name, gsi_name, reads, writes))

    # Check that we are in the right time frame
    m_windows = get_gsi_option(table_key, gsi_key, 'maintenance_windows')
    if m_windows:
        if not __is_gsi_maintenance_window(table_name, gsi_name, m_windows):
            logger.warning(
                '{0} - GSI: {1} - We are outside a maintenace window. '
                'Will only perform up scaling activites'.format(
                    table_name,
                    gsi_name))

            # Ensure that we are only doing increases
            if current_reads > reads:
                reads = current_reads
            if current_writes > writes:
                writes = current_writes

            # Return if we do not need to scale up
            if reads == current_reads and writes == current_writes:
                logger.info(
                    '{0} - GSI: {1} - '
                    'No need to scale up reads nor writes'.format(
                        table_name,
                        gsi_name))
                return

        else:
            logger.info(
                '{0} - GSI: {1} - '
                'Current time is within maintenance window'.format(
                    table_name,
                    gsi_name))

    logger.info(
        '{0} - GSI: {1} - '
        'Updating provisioning to {2} reads and {3} writes'.format(
            table_name, gsi_name, reads, writes))

    # Return if dry-run
    if get_global_option('dry_run'):
        return

    try:
        DYNAMODB_CONNECTION.update_table(
            table_name=table_name,
            global_secondary_index_updates=[
                {
                    "Update": {
                        "IndexName": gsi_name,
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": reads,
                            "WriteCapacityUnits": writes
                        }
                    }
                }
            ])

        message = []
        if current_reads > reads:
            message.append(
                '{0} - GSI: {1} - Reads: DOWN from {2} to {3}\n'.format(
                    table_name, gsi_name, current_reads, reads))
        elif current_reads < reads:
            message.append(
                '{0} - GSI: {1} - Reads: UP from {2} to {3}\n'.format(
                    table_name, gsi_name, current_reads, reads))
        if current_writes > writes:
            message.append(
                '{0} - GSI: {1} - Writes: DOWN from {2} to {3}\n'.format(
                    table_name, gsi_name, current_writes, writes))
        elif current_writes < writes:
            message.append(
                '{0} - GSI: {1} - Writes: UP from {2} to {3}\n'.format(
                    table_name, gsi_name, current_writes, writes))

        # See if we should send notifications for scale-down, scale-up or both
        sns_message_types = []
        if current_reads > reads or current_writes > writes:
            sns_message_types.append('scale-down')
        if current_reads < reads or current_writes < writes:
            sns_message_types.append('scale-up')

        sns.publish_gsi_notification(
            table_key,
            gsi_key,
            ''.join(message),
            sns_message_types,
            subject='Updated provisioning for GSI {0}'.format(gsi_name))

    except JSONResponseError as error:
        exception = error.body['__type'].split('#')[1]
        know_exceptions = ['LimitExceededException']
        if exception in know_exceptions:
            logger.warning('{0} - GSI: {1} - {2}: {3}'.format(
                table_name, gsi_name, exception, error.body['message']))
        else:
            logger.error(
                (
                    '{0} - GSI: {1} - Unhandled exception: {2}: {3}. '
                    'Please file a bug report at '
                    'https://github.com/sebdah/dynamic-dynamodb/issues'
                ).format(
                    table_name, gsi_name, exception, error.body['message']))

        if (not retry_with_only_increase and
                exception == 'LimitExceededException'):
            logger.info(
                '{0} - GSI: {1} - Will retry to update provisioning '
                'with only increases'.format(table_name, gsi_name))
            update_gsi_provisioning(
                table_name,
                table_key,
                gsi_name,
                gsi_key,
                reads,
                writes,
                retry_with_only_increase=True)


def table_gsis(table_name):
    """ Returns a list of GSIs for the given table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: list -- List of GSI names
    """
    try:
        desc = DYNAMODB_CONNECTION.describe_table(table_name)[u'Table']
    except JSONResponseError:
        raise

    if u'GlobalSecondaryIndexes' in desc:
        return desc[u'GlobalSecondaryIndexes']

    return []


def __get_connection_dynamodb(retries=3):
    """ Ensure connection to DynamoDB

    :type retries: int
    :param retries: Number of times to retry to connect to DynamoDB
    """
    connected = False
    region = get_global_option('region')

    while not connected:
        if (get_global_option('aws_access_key_id') and
                get_global_option('aws_secret_access_key')):
            logger.debug(
                'Authenticating to DynamoDB using '
                'credentials in configuration file')
            connection = dynamodb2.connect_to_region(
                region,
                aws_access_key_id=get_global_option('aws_access_key_id'),
                aws_secret_access_key=get_global_option(
                    'aws_secret_access_key'))
        else:
            logger.debug(
                'Authenticating using boto\'s authentication handler')
            connection = dynamodb2.connect_to_region(region)

        if not connection:
            if retries == 0:
                logger.error('Failed to connect to DynamoDB. Giving up.')
                raise
            else:
                logger.error(
                    'Failed to connect to DynamoDB. Retrying in 5 seconds')
                retries -= 1
                time.sleep(5)
        else:
            connected = True
            logger.debug('Connected to DynamoDB in {0}'.format(region))

    return connection


def __is_gsi_maintenance_window(table_name, gsi_name, maintenance_windows):
    """ Checks that the current time is within the maintenance window

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type maintenance_windows: str
    :param maintenance_windows: Example: '00:00-01:00,10:00-11:00'
    :returns: bool -- True if within maintenance window
    """
    # Example string '00:00-01:00,10:00-11:00'
    maintenance_window_list = []
    for window in maintenance_windows.split(','):
        try:
            start, end = window.split('-', 1)
        except ValueError:
            logger.error(
                '{0} - GSI: {1} - '
                'Malformatted maintenance window'.format(table_name, gsi_name))
            return False

        maintenance_window_list.append((start, end))

    now = datetime.datetime.utcnow().strftime('%H%M')
    for maintenance_window in maintenance_window_list:
        start = ''.join(maintenance_window[0].split(':'))
        end = ''.join(maintenance_window[1].split(':'))
        if now >= start and now <= end:
            return True

    return False


def __is_table_maintenance_window(table_name, maintenance_windows):
    """ Checks that the current time is within the maintenance window

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type maintenance_windows: str
    :param maintenance_windows: Example: '00:00-01:00,10:00-11:00'
    :returns: bool -- True if within maintenance window
    """
    # Example string '00:00-01:00,10:00-11:00'
    maintenance_window_list = []
    for window in maintenance_windows.split(','):
        try:
            start, end = window.split('-', 1)
        except ValueError:
            logger.error(
                '{0} - Malformatted maintenance window'.format(table_name))
            return False

        maintenance_window_list.append((start, end))

    now = datetime.datetime.utcnow().strftime('%H%M')
    for maintenance_window in maintenance_window_list:
        start = ''.join(maintenance_window[0].split(':'))
        end = ''.join(maintenance_window[1].split(':'))
        if now >= start and now <= end:
            return True

    return False

DYNAMODB_CONNECTION = __get_connection_dynamodb()
