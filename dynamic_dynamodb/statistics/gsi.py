""" This module returns stats about the DynamoDB table """
import math
from datetime import datetime, timedelta

from dynamic_dynamodb.core import dynamodb
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.core.cloudwatch import (
    CLOUDWATCH_CONNECTION as cloudwatch_connection)


def get_consumed_read_units_percent(table_name, gsi_name, time_frame=300):
    """ Returns the number of consumed read units in percent

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
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
        dimensions={
            'TableName': table_name,
            'GlobalSecondaryIndexName': gsi_name
        },
        unit='Count')

    if metrics:
        consumed_read_units = int(
            math.ceil(float(metrics[0]['Sum'])/float(time_frame)))
    else:
        consumed_read_units = 0

    consumed_read_units_percent = int(
        math.ceil(
            float(consumed_read_units) /
            float(dynamodb.get_provisioned_gsi_read_units(
                table_name, gsi_name)) * 100))

    logger.info('{0} - GSI: {1} - Consumed read units: {2:d}%'.format(
        table_name, gsi_name, consumed_read_units_percent))
    return consumed_read_units_percent


def get_consumed_write_units_percent(table_name, gsi_name, time_frame=300):
    """ Returns the number of consumed write units in percent

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
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
        dimensions={
            'TableName': table_name,
            'GlobalSecondaryIndexName': gsi_name
        },
        unit='Count')

    if metrics:
        consumed_write_units = int(
            math.ceil(float(metrics[0]['Sum'])/float(time_frame)))
    else:
        consumed_write_units = 0

    consumed_write_units_percent = int(
        math.ceil(
            float(consumed_write_units) /
            float(dynamodb.get_provisioned_gsi_write_units(
                table_name, gsi_name)) * 100))

    logger.info('{0} - GSI: {1} - Consumed write units: {2:d}%'.format(
        table_name, gsi_name, consumed_write_units_percent))
    return consumed_write_units_percent
