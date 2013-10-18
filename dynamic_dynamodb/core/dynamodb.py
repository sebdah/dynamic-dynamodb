""" Handle most tasks related to DynamoDB interaction """
import time

from boto import dynamodb
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
        try:
            if (configuration['global']['aws_access_key_id'] and
                    configuration['global']['aws_secret_access_key']):
                connection = dynamodb.connect_to_region(
                    configuration['global']['region'],
                    aws_access_key_id=
                    configuration['global']['aws_access_key_id'],
                    aws_secret_access_key=
                    configuration['global']['aws_secret_access_key'])
            else:
                connection = dynamodb.connect_to_region(
                    configuration['global']['region'])
            connected = True

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

    logger.debug('Connected to DynamoDB')
    return connection


def get_table(table_name):
    """ Return the DynamoDB table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: boto.dynamodb.table.Table
    """
    try:
        table = DYNAMODB_CONNECTION.get_table(table_name)
    except DynamoDBResponseError as error:
        dynamodb_error = error.body['__type'].rsplit('#', 1)[1]
        if dynamodb_error == 'ResourceNotFoundException':
            logger.error(
                '{0} - Table {1} not found'.format(table_name, table_name))

        raise

    return table


def list_tables():
    """ Return list of DynamoDB tables available from AWS

    :returns: list -- List of DynamoDB tables
    """
    tables = []

    try:
        tables = DYNAMODB_CONNECTION.list_tables()
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


DYNAMODB_CONNECTION = __get_connection_dynamodb()
