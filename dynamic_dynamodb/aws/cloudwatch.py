# -*- coding: utf-8 -*-
""" Ensure connections to CloudWatch """
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_global_option

from boto.ec2 import cloudwatch


def __get_connection_cloudwatch():
    """ Ensure connection to CloudWatch """
    region = get_global_option('region')
    try:
        if (get_global_option('aws_access_key_id') and
                get_global_option('aws_secret_access_key')):
            logger.debug(
                'Authenticating to CloudWatch using '
                'credentials in configuration file')
            connection = cloudwatch.connect_to_region(
                region,
                aws_access_key_id=get_global_option('aws_access_key_id'),
                aws_secret_access_key=get_global_option(
                    'aws_secret_access_key'))
        else:
            logger.debug(
                'Authenticating using boto\'s authentication handler')
            connection = cloudwatch.connect_to_region(region)

    except Exception as err:
        logger.error('Failed connecting to CloudWatch: {0}'.format(err))
        logger.error(
            'Please report an issue at: '
            'https://github.com/sebdah/dynamic-dynamodb/issues')
        raise

    logger.debug('Connected to CloudWatch in {0}'.format(region))
    return connection


CLOUDWATCH_CONNECTION = __get_connection_cloudwatch()
