""" Handle most tasks related to DynamoDB interaction """
import time
import sys

from boto import dynamodb2
from boto.dynamodb2.table import Table
from boto.exception import DynamoDBResponseError, JSONResponseError

from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import CONFIGURATION as configuration


def __get_connection_dynamodb(retries=3):
    """ Ensure connection to DynamoDB

    :type retries: int
    :param retries: Number of times to retry to connect to DynamoDB
    """
    connected = False
    while not connected:
        logger.debug('Connecting to DynamoDB in {0}'.format(
            configuration['global']['region']))

        if (configuration['global']['aws_access_key_id'] and
                configuration['global']['aws_secret_access_key']):
            connection = dynamodb2.connect_to_region(
                configuration['global']['region'],
                aws_access_key_id=
                configuration['global']['aws_access_key_id'],
                aws_secret_access_key=
                configuration['global']['aws_secret_access_key'])
        else:
            connection = dynamodb2.connect_to_region(
                configuration['global']['region'])

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
            logger.debug('Connected to DynamoDB in {0}'.format(
                configuration['global']['region']))

    return connection


def describe_table(table_name):
    """ Return table details

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: dict
    """
    return DYNAMODB_CONNECTION.describe_table(table_name)


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
    desc = DYNAMODB_CONNECTION.describe_table(table_name)
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
    desc = DYNAMODB_CONNECTION.describe_table(table_name)
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
    desc = DYNAMODB_CONNECTION.describe_table(table_name)
    for gsi in desc[u'Table'][u'GlobalSecondaryIndexes']:
        if gsi[u'IndexName'] == gsi_name:
            write_units = int(
                gsi[u'ProvisionedThroughput'][u'WriteCapacityUnits'])
            break

    logger.debug(
        '{0} - GSI: {1} - Currently povisioned write units: {2:d}'.format(
            table_name, gsi_name, write_units))
    return write_units


def get_provisioned_table_read_units(table_name):
    """ Returns the number of provisioned read units for the table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: int -- Number of read units
    """
    desc = DYNAMODB_CONNECTION.describe_table(table_name)
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
    desc = DYNAMODB_CONNECTION.describe_table(table_name)
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
    desc = DYNAMODB_CONNECTION.describe_table(table_name)
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
        logger.error('Communication error: {0}'.format(error.body['message']))
        sys.exit(1)

    return tables


def update_table_provisioning(
        table_name, reads, writes, retry_with_only_increase=False):
    """ Update provisioning for a given table

    :type table_name: str
    :param table_name: Name of the table
    :type reads: int
    :param reads: New number of provisioned read units
    :type writes: int
    :param writes: New number of provisioned write units
    :type retry_with_only_increase: bool
    :param retry_with_only_increase: Set to True to ensure only increases
    """
    table = get_table(table_name)

    if retry_with_only_increase:
        current_reads = int(get_provisioned_table_read_units(table_name))
        current_writes = int(get_provisioned_table_write_units(table_name))

        # Ensure that we are only doing increases
        if current_reads > reads:
            reads = current_reads
        if current_writes > writes:
            writes = current_writes

        logger.info(
            '{0} - Retrying to update provisioning, excluding any decreases. '
            'Setting new reads to {1} and new writes to {2}'.format(
                table_name, reads, writes))

    try:
        table.update(
            throughput={
                'read': reads,
                'write': writes
            })
        logger.info(
            '{0} - Provisioning updated to {1} reads and {2} writes'.format(
                table_name, reads, writes))
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
            logger.error(
                (
                    '{0} - Unhandled exception: {1}: {2}. '
                    'Please file a bug report at '
                    'https://github.com/sebdah/dynamic-dynamodb/issues'
                ).format(table_name, exception, error.body['message']))

        if (not retry_with_only_increase and
                exception == 'LimitExceededException'):
            logger.info(
                '{0} - Will retry to update provisioning '
                'with only increases'.format(table_name))
            update_table_provisioning(
                table_name,
                reads,
                writes,
                retry_with_only_increase=True)


def update_gsi_provisioning(
        table_name, gsi_name, reads, writes, retry_with_only_increase=False):
    """ Update provisioning on a global secondary index

    :type table_name: str
    :param table_name: Name of the table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type reads: int
    :param reads: Number of reads to provision
    :type writes: int
    :param writes: Number of writes to provision
    :type retry_with_only_increase: bool
    :param retry_with_only_increase: Set to True to ensure only increases
    """
    if retry_with_only_increase:
        current_reads = int(get_provisioned_table_read_units(table_name))
        current_writes = int(get_provisioned_table_write_units(table_name))

        # Ensure that we are only doing increases
        if current_reads > reads:
            reads = current_reads
        if current_writes > writes:
            writes = current_writes

        logger.info(
            '{0} - Retrying to update provisioning, excluding any decreases. '
            'Setting new reads to {1} and new writes to {2}'.format(
                table_name, reads, writes))

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
                gsi_name,
                reads,
                writes,
                retry_with_only_increase=True)


def table_gsis(table_name):
    """ Returns a list of GSIs for the given table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: list -- List of GSI names
    """
    desc = DYNAMODB_CONNECTION.describe_table(table_name)[u'Table']

    if u'GlobalSecondaryIndexes' in desc:
        return desc[u'GlobalSecondaryIndexes']

    return []

DYNAMODB_CONNECTION = __get_connection_dynamodb()
