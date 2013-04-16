# -*- coding: utf-8 -*-
""" Ensure connections to DynamoDB and CloudWatch """
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import CONFIGURATION as configuration

from boto.ec2 import cloudwatch


def __get_connection_cloudwatch():
    """ Ensure connection to CloudWatch """
    try:
        if (configuration['global']['aws_access_key_id'] and
            configuration['global']['aws_secret_access_key']):
            connection = cloudwatch.connect_to_region(
                configuration['global']['region'],
                aws_access_key_id=configuration['global']['aws_access_key_id'],
                aws_secret_access_key=\
                    configuration['global']['aws_secret_access_key'])
        else:
            connection = cloudwatch.connect_to_region(
                configuration['global']['region'])

    except Exception as err:
        logger.error('Failed connecting to CloudWatch: {0}'.format(err))
        logger.error(
            'Please report an issue at: '
            'https://github.com/sebdah/dynamic-dynamodb/issues')
        raise

    logger.debug('Connected to CloudWatch')
    return connection



CLOUDWATCH_CONNECTION = __get_connection_cloudwatch()
