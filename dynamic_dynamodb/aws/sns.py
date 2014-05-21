# -*- coding: utf-8 -*-
""" Handles SNS connection and communication """
from boto import sns
from boto.exception import BotoServerError
from boto.utils import get_instance_metadata

from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import (
    get_gsi_option, get_table_option, get_global_option)


def publish_gsi_notification(
        table_key, gsi_key, message, message_types, subject=None):
    """ Publish a notification for a specific GSI

    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_key: str
    :param gsi_key: Table configuration option key name
    :type message: str
    :param message: Message to send via SNS
    :type message_types: list
    :param message_types: List with types: scale-up, scale-down, error-message
    :type subject: str
    :param subject: Subject to use for e-mail notifications
    :returns: None
    """
    topic = get_gsi_option(table_key, gsi_key, 'sns_topic_arn')
    if not topic:
        return

    for message_type in message_types:
        if (message_type in
                get_gsi_option(table_key, gsi_key, 'sns_message_types')):
            __publish(topic, message, subject)
            return


def publish_table_notification(table_key, message, message_types, subject=None):
    """ Publish a notification for a specific table

    :type table_key: str
    :param table_key: Table configuration option key name
    :type message: str
    :param message: Message to send via SNS
    :type message_types: list
    :param message_types: List with types: scale-up, scale-down, error-message
    :type subject: str
    :param subject: Subject to use for e-mail notifications
    :returns: None
    """
    topic = get_table_option(table_key, 'sns_topic_arn')
    if not topic:
        return

    for message_type in message_types:
        if message_type in get_table_option(table_key, 'sns_message_types'):
            __publish(topic, message, subject)
            return


def __publish(topic, message, subject=None):
    """ Publish a message to a SNS topic

    :type topic: str
    :param topic: SNS topic to publish the message to
    :type message: str
    :param message: Message to send via SNS
    :type subject: str
    :param subject: Subject to use for e-mail notifications
    :returns: None
    """
    try:
        SNS_CONNECTION.publish(topic=topic, message=message, subject=subject)
        logger.info('Sent SNS notification to {0}'.format(topic))
    except BotoServerError as error:
        logger.error('Problem sending SNS notification: {0}'.format(
            error.message))

    return


def __get_connection_SNS():
    """ Ensure connection to SNS """
    try:
        if (get_global_option('aws_access_key_id') and
                get_global_option('aws_secret_access_key')):
            logger.debug(
                'Authenticating to SNS using '
                'credentials in configuration file')
            region = get_global_option('region')
            connection = sns.connect_to_region(
                region,
                aws_access_key_id=get_global_option(
                    'aws_access_key_id'),
                aws_secret_access_key=get_global_option(
                    'aws_secret_access_key'))
        else:
            try:
                logger.debug(
                    'Authenticating to SNS using EC2 instance profile')
                metadata = get_instance_metadata(timeout=1, num_retries=1)
                region = metadata['placement']['availability-zone'][:-1]
                connection = sns.connect_to_region(
                    region,
                    profile_name=metadata['iam']['info'][u'InstanceProfileArn'])
            except KeyError:
                logger.debug(
                    'Authenticating to SNS using '
                    'env vars / boto configuration')
                region = get_global_option('region')
                connection = sns.connect_to_region(region)

    except Exception as err:
        logger.error('Failed connecting to SNS: {0}'.format(err))
        logger.error(
            'Please report an issue at: '
            'https://github.com/sebdah/dynamic-dynamodb/issues')
        raise

    logger.debug('Connected to SNS in {0}'.format(region))
    return connection

SNS_CONNECTION = __get_connection_SNS()
