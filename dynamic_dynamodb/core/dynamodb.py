""" Handle most tasks related to DynamoDB interaction """
import time

from boto import dynamodb2
from boto.dynamodb2.table import Table
from boto.exception import DynamoDBResponseError

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
        try:
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
            connected = True
            logger.debug('Connected to DynamoDB in {0}'.format(
                configuration['global']['region']))

        except Exception as err:
            logger.error('Failed to connect to DynamoDB: {0}'.format(err))
            if retries == 0:
                logger.error(
                    'Please report an issue at: '
                    'https://github.com/sebdah/dynamic-dynamodb/issues')
                raise
            else:
                logger.error('Retrying in 5 seconds')
                retries -= 1
                time.sleep(5)

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
        for table_name in DYNAMODB_CONNECTION.list_tables()[u'TableNames']:
            tables.append(get_table(table_name))
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

    return tables


def update_gsi_provisioning(table_name, gsi_name, reads, writes):
    """ Update provisioning on a global secondary index

    :type table_name: str
    :param table_name: Name of the table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type reads: int
    :param reads: Number of reads to provision
    :type writes: int
    :param writes: Number of writes to provision
    """
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
