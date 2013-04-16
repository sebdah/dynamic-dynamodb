""" Handle most tasks related to DynamoDB interaction """
import sys

from boto import dynamodb
from boto.exception import DynamoDBResponseError

from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import CONFIGURATION as configuration


def __get_connection_dynamodb():
    """ Ensure connection to DynamoDB """
    try:
        if (configuration['global']['aws_access_key_id'] and
            configuration['global']['aws_secret_access_key']):
            connection = dynamodb.connect_to_region(
                configuration['global']['region'],
                aws_access_key_id=configuration['global']['aws_access_key_id'],
                aws_secret_access_key=\
                    configuration['global']['aws_secret_access_key'])
        else:
            connection = dynamodb.connect_to_region(
                configuration['global']['region'])

    except Exception as err:
        logger.error('Failed connecting to DynamoDB: {0}'.format(err))
        logger.error(
            'Please report an issue at: '
            'https://github.com/sebdah/dynamic-dynamodb/issues')
        raise

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
            sys.exit(1)
        else:
            raise

    return table

DYNAMODB_CONNECTION = __get_connection_dynamodb()
