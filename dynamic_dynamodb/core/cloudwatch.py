# -*- coding: utf-8 -*-
""" Ensure connections to DynamoDB and CloudWatch """
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import CONFIGURATION as configuration

from boto.ec2 import cloudwatch
from boto.utils import get_instance_metadata


def __get_connection_cloudwatch():
    """ Ensure connection to SNS """
    try:
        if (configuration['global']['aws_access_key_id'] and
                configuration['global']['aws_secret_access_key']):
            logger.debug(
                'Authenticating to CloudWatch using '
                'credentials in configuration file')
            connection = cloudwatch.connect_to_region(
                configuration['global']['region'],
                aws_access_key_id=configuration['global']['aws_access_key_id'],
                aws_secret_access_key=
                configuration['global']['aws_secret_access_key'])
        else:
            try:
                logger.debug(
                    'Authenticating to CloudWatch using EC2 instance profile')
                metadata = get_instance_metadata(timeout=1, num_retries=1)
                connection = cloudwatch.connect_to_region(
                    metadata['placement']['availability-zone'][:-1],
                    profile_name=metadata['iam']['info'][u'InstanceProfileArn'])
            except KeyError:
                logger.debug(
                    'Authenticating to CloudWatch using '
                    'env vars / boto configuration')
                connection = cloudwatch.connect_to_region(
                    configuration['global']['region'])

    except Exception as err:
        logger.error('Failed connecting to CloudWatch: {0}'.format(err))
        logger.error(
            'Please report an issue at: '
            'https://github.com/sebdah/dynamic-dynamodb/issues')
        raise

    logger.debug('Connected to CloudWatch in {0}'.format(
        configuration['global']['region']))
    return connection


CLOUDWATCH_CONNECTION = __get_connection_cloudwatch()
