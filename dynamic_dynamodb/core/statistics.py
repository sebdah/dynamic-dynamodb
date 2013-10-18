""" This module returns stats about the DynamoDB table """
import math
from datetime import datetime, timedelta

from boto.exception import DynamoDBResponseError

import dynamodb
from dynamic_dynamodb.log_handler import LOGGER as logger
from cloudwatch import CLOUDWATCH_CONNECTION as cloudwatch_connection


def get_consumed_read_units(table_name, time_frame=300):
    """ Returns the number of consumed read units

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type time_frame: int
    :param time_frame: How many seconds to look at
    :returns: int -- Number of consumed reads
    """
    metrics = cloudwatch_connection.get_metric_statistics(
        time_frame,
        datetime.utcnow()-timedelta(minutes=10, seconds=time_frame),
        datetime.utcnow()-timedelta(minutes=10),
        'ConsumedReadCapacityUnits',
        'AWS/DynamoDB',
        ['Sum'],
        dimensions={'TableName': table_name},
        unit='Count')

    if metrics:
        consumed_read_units = int(
            math.ceil(float(metrics[0]['Sum'])/float(time_frame)))
    else:
        consumed_read_units = 0

    logger.info('{0} - Consumed read units: {1:d}'.format(
        table_name, consumed_read_units))
    return consumed_read_units


def get_consumed_write_units(table_name, time_frame=300):
    """ Returns the number of consumed write units

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type time_frame: int
    :param time_frame: How many seconds to look at
    :returns: int -- Number of consumed writes
    """
    metrics = cloudwatch_connection.get_metric_statistics(
        time_frame,
        datetime.utcnow()-timedelta(minutes=10, seconds=time_frame),
        datetime.utcnow()-timedelta(minutes=10),
        'ConsumedWriteCapacityUnits',
        'AWS/DynamoDB',
        ['Sum'],
        dimensions={'TableName': table_name},
        unit='Count')

    if metrics:
        consumed_write_units = int(
            math.ceil(float(metrics[0]['Sum'])/float(time_frame)))
    else:
        consumed_write_units = 0

    logger.info('{0} - Consumed write units: {1:d}'.format(
        table_name, consumed_write_units))
    return consumed_write_units


def get_consumed_read_units_percent(table_name, time_frame=300):
    """ Returns the number of consumed read units in percent

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type time_frame: int
    :param time_frame: How many seconds to look at
    :returns: int -- Number of consumed reads
    """
    metrics = cloudwatch_connection.get_metric_statistics(
        period=time_frame,
        start_time=datetime.utcnow()-timedelta(minutes=10, seconds=time_frame),
        end_time=datetime.utcnow()-timedelta(minutes=10),
        metric_name='ConsumedReadCapacityUnits',
        namespace='AWS/DynamoDB',
        statistics=['Sum'],
        dimensions={'TableName': table_name},
        unit='Count')

    if metrics:
        consumed_read_units = int(
            math.ceil(float(metrics[0]['Sum'])/float(time_frame)))
    else:
        consumed_read_units = 0

    consumed_read_units_percent = int(
        math.ceil(
            float(consumed_read_units) /
            float(get_provisioned_read_units(table_name)) * 100))

    logger.info('{0} - Consumed read units: {1:d}%'.format(
        table_name, consumed_read_units_percent))
    return consumed_read_units_percent


def get_consumed_write_units_percent(table_name, time_frame=300):
    """ Returns the number of consumed write units in percent

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type time_frame: int
    :param time_frame: How many seconds to look at
    :returns: int -- Number of consumed writes
    """
    metrics = cloudwatch_connection.get_metric_statistics(
        period=time_frame,
        start_time=datetime.utcnow()-timedelta(minutes=10, seconds=time_frame),
        end_time=datetime.utcnow()-timedelta(minutes=10),
        metric_name='ConsumedWriteCapacityUnits',
        namespace='AWS/DynamoDB',
        statistics=['Sum'],
        dimensions={'TableName': table_name},
        unit='Count')

    if metrics:
        consumed_write_units = int(
            math.ceil(float(metrics[0]['Sum'])/float(time_frame)))
    else:
        consumed_write_units = 0

    consumed_write_units_percent = int(
        math.ceil(
            float(consumed_write_units) /
            float(get_provisioned_write_units(table_name)) * 100))

    logger.info('{0} - Consumed write units: {1:d}%'.format(
        table_name, consumed_write_units_percent))
    return consumed_write_units_percent


def get_provisioned_read_units(table_name):
    """ Returns the number of provisioned read units for the table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: int -- Number of read units
    """
    try:
        table = dynamodb.get_table(table_name)
    except DynamoDBResponseError:
        # Return if the table does not exist
        return None

    logger.debug('{0} - Provisioned read units: {1:d}'.format(
        table_name, table.read_units))
    return int(table.read_units)


def get_provisioned_write_units(table_name):
    """ Returns the number of provisioned write units for the table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: int -- Number of write units
    """
    try:
        table = dynamodb.get_table(table_name)
    except DynamoDBResponseError:
        # Return if the table does not exist
        return None

    logger.debug('{0} - Provisioned write units: {1:d}'.format(
        table_name, table.write_units))
    return int(table.write_units)
