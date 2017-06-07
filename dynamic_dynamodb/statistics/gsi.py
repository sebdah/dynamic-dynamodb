# -*- coding: utf-8 -*-
""" This module returns stats about the DynamoDB table """
from datetime import datetime, timedelta

from boto.exception import JSONResponseError, BotoServerError
from retrying import retry

from dynamic_dynamodb.aws import dynamodb
from dynamic_dynamodb.aws.cloudwatch import (
    CLOUDWATCH_CONNECTION as cloudwatch_connection)


def get_consumed_read_units_percent(logger,
        table_name, gsi_name, lookback_window_start=15, lookback_period=5):
    """ Returns the number of consumed read units in percent

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type lookback_window_start: int
    :param lookback_window_start: Relative start time for the CloudWatch metric
    :type lookback_period: int
    :param lookback_period: Number of minutes to look at
    :returns: float -- Number of consumed reads as a
        percentage of provisioned reads
    """
    try:
        metrics = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'ConsumedReadCapacityUnits')
    except BotoServerError:
        raise

    if metrics:
        lookback_seconds = lookback_period * 60
        consumed_read_units = (
            float(metrics[0]['Sum']) / float(lookback_seconds))
    else:
        consumed_read_units = 0

    try:
        gsi_read_units = dynamodb.get_provisioned_gsi_read_units(
            table_name, gsi_name)

        consumed_read_units_percent = (
            float(consumed_read_units) /
            float(gsi_read_units) * 100)
    except JSONResponseError:
        raise

    logger.info('{0} - GSI: {1} - Consumed read units: {2:.2f}%'.format(
        table_name, gsi_name, consumed_read_units_percent))
    return consumed_read_units_percent


def get_throttled_read_event_count(logger,
        table_name, gsi_name, lookback_window_start=15, lookback_period=5):
    """ Returns the number of throttled read events during a given time frame

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type lookback_window_start: int
    :param lookback_window_start: Relative start time for the CloudWatch metric
    :type lookback_period: int
    :param lookback_period: Number of minutes to look at
    :returns: int -- Number of throttled read events during the time period
    """
    try:
        metrics = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'ReadThrottleEvents')
    except BotoServerError:
        raise

    if metrics:
        throttled_read_events = int(metrics[0]['Sum'])
    else:
        throttled_read_events = 0

    logger.info('{0} - GSI: {1} - Read throttle count: {2:d}'.format(
        table_name, gsi_name, throttled_read_events))
    return throttled_read_events


def get_throttled_by_provisioned_read_event_percent(logger,
        table_name, gsi_name, lookback_window_start=15, lookback_period=5):
    """ Returns the number of throttled read events in percent

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type lookback_window_start: int
    :param lookback_window_start: Relative start time for the CloudWatch metric
    :type lookback_period: int
    :param lookback_period: Number of minutes to look at
    :returns: float -- Percent of throttled read events by provisioning
    """
    try:
        metrics = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'ReadThrottleEvents')
    except BotoServerError:
        raise

    if metrics:
        lookback_seconds = lookback_period * 60
        throttled_read_events = (
            float(metrics[0]['Sum']) / float(lookback_seconds))
    else:
        throttled_read_events = 0

    try:
        gsi_read_units = dynamodb.get_provisioned_gsi_read_units(
            table_name, gsi_name)

        throttled_by_provisioned_read_percent = (
            float(throttled_read_events) /
            float(gsi_read_units) * 100)
    except JSONResponseError:
        raise

    logger.info(
        '{0} - GSI: {1} - Throttled read percent '
        'by provision: {2:.2f}%'.format(
            table_name, gsi_name, throttled_by_provisioned_read_percent))
    return throttled_by_provisioned_read_percent


def get_throttled_by_consumed_read_percent(logger,
        table_name, gsi_name, lookback_window_start=15, lookback_period=5):
    """ Returns the number of throttled read events in percent of consumption

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type lookback_window_start: int
    :param lookback_window_start: Relative start time for the CloudWatch metric
    :type lookback_period: int
    :param lookback_period: Number of minutes to look at
    :returns: float -- Percent of throttled read events by consumption
    """

    try:
        metrics1 = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'ConsumedReadCapacityUnits')
        metrics2 = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'ReadThrottleEvents')
    except BotoServerError:
        raise

    if metrics1 and metrics2:
        lookback_seconds = lookback_period * 60
        throttled_by_consumed_read_percent = (
            (
                (float(metrics2[0]['Sum']) / float(lookback_seconds)) /
                (float(metrics1[0]['Sum']) / float(lookback_seconds))
            ) * 100)
    else:
        throttled_by_consumed_read_percent = 0

    logger.info(
        '{0} - GSI: {1} - Throttled read percent '
        'by consumption: {2:.2f}%'.format(
            table_name, gsi_name, throttled_by_consumed_read_percent))
    return throttled_by_consumed_read_percent


def get_consumed_write_units_percent(logger,
        table_name, gsi_name, lookback_window_start=15, lookback_period=5):
    """ Returns the number of consumed write units in percent

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type lookback_window_start: int
    :param lookback_window_start: Relative start time for the CloudWatch metric
    :type lookback_period: int
    :param lookback_period: Number of minutes to look at
    :returns: float -- Number of consumed writes as a
        percentage of provisioned writes
    """
    try:
        metrics = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'ConsumedWriteCapacityUnits')
    except BotoServerError:
        raise

    if metrics:
        lookback_seconds = lookback_period * 60
        consumed_write_units = (
            float(metrics[0]['Sum']) / float(lookback_seconds))
    else:
        consumed_write_units = 0

    try:
        gsi_write_units = dynamodb.get_provisioned_gsi_write_units(
            table_name, gsi_name)

        consumed_write_units_percent = (
            float(consumed_write_units) /
            float(gsi_write_units) * 100)
    except JSONResponseError:
        raise

    logger.info('{0} - GSI: {1} - Consumed write units: {2:.2f}%'.format(
        table_name, gsi_name, consumed_write_units_percent))
    return consumed_write_units_percent


def get_throttled_write_event_count(logger,
        table_name, gsi_name, lookback_window_start=15, lookback_period=5):
    """ Returns the number of throttled write events during a given time frame

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type lookback_window_start: int
    :param lookback_window_start: Relative start time for the CloudWatch metric
    :type lookback_period: int
    :param lookback_period: Number of minutes to look at
    :returns: int -- Number of throttled write events during the time period
    """
    try:
        metrics = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'WriteThrottleEvents')
    except BotoServerError:
        raise

    if metrics:
        throttled_write_events = int(metrics[0]['Sum'])
    else:
        throttled_write_events = 0

    logger.info('{0} - GSI: {1} - Write throttle count: {2:d}'.format(
        table_name, gsi_name, throttled_write_events))
    return throttled_write_events


def get_throttled_by_provisioned_write_event_percent(logger,
        table_name, gsi_name, lookback_window_start=15, lookback_period=5):
    """ Returns the number of throttled write events during a given time frame

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type lookback_window_start: int
    :param lookback_window_start: Relative start time for the CloudWatch metric
    :type lookback_period: int
    :param lookback_period: Number of minutes to look at
    :returns: float -- Percent of throttled write events by provisioning
    """
    try:
        metrics = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'WriteThrottleEvents')
    except BotoServerError:
        raise

    if metrics:
        lookback_seconds = lookback_period * 60
        throttled_write_events = float(metrics[0]['Sum']) / float(
            lookback_seconds)
    else:
        throttled_write_events = 0

    try:
        gsi_write_units = dynamodb.get_provisioned_gsi_write_units(
            table_name, gsi_name)

        throttled_by_provisioned_write_percent = (
            float(throttled_write_events) /
            float(gsi_write_units) * 100)
    except JSONResponseError:
        raise

    logger.info(
        '{0} - GSI: {1} - Throttled write percent '
        'by provision: {2:.2f}%'.format(
            table_name, gsi_name, throttled_by_provisioned_write_percent))
    return throttled_by_provisioned_write_percent


def get_throttled_by_consumed_write_percent(logger,
        table_name, gsi_name, lookback_window_start=15, lookback_period=5):
    """ Returns the number of throttled write events in percent of consumption

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type lookback_window_start: int
    :param lookback_window_start: Relative start time for the CloudWatch metric
    :type lookback_period: int
    :param lookback_period: Number of minutes to look at
    :returns: float -- Percent of throttled write events by consumption
    """

    try:
        metrics1 = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'ConsumedWriteCapacityUnits')
        metrics2 = __get_aws_metric(logger,
            table_name,
            gsi_name,
            lookback_window_start,
            lookback_period,
            'WriteThrottleEvents')

    except BotoServerError:
        raise

    if metrics1 and metrics2:
        lookback_seconds = lookback_period * 60
        throttled_by_consumed_write_percent = (
            (
                (float(metrics2[0]['Sum']) / float(lookback_seconds)) /
                (float(metrics1[0]['Sum']) / float(lookback_seconds))
            ) * 100)
    else:
        throttled_by_consumed_write_percent = 0

    logger.info(
        '{0} - GSI: {1} - Throttled write percent '
        'by consumption: {2:.2f}%'.format(
            table_name, gsi_name, throttled_by_consumed_write_percent))
    return throttled_by_consumed_write_percent


@retry(
    wait='exponential_sleep',
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000,
    stop_max_attempt_number=10)
def __get_aws_metric(logger, table_name,
                     gsi_name,
                     lookback_window_start,
                     lookback_period,
                     metric_name):
    """ Returns a  metric list from the AWS CloudWatch service, may return
    None if no metric exists

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of a GSI on the given DynamoDB table
    :type lookback_window_start: int
    :param lookback_window_start: How many minutes to look at
    :type lookback_period: int
    :type lookback_period: Length of the lookback period in minutes
    :type metric_name: str
    :param metric_name: Name of the metric to retrieve from CloudWatch
    :returns: list --
        A list of time series data for the given metric, may be None if
        there was no data
    """
    try:
        now = datetime.utcnow()
        start_time = now - timedelta(minutes=lookback_window_start)
        end_time = now - timedelta(
            minutes=lookback_window_start - lookback_period)

        return cloudwatch_connection.get_metric_statistics(
            period=lookback_period * 60,
            start_time=start_time,
            end_time=end_time,
            metric_name=metric_name,
            namespace='AWS/DynamoDB',
            statistics=['Sum'],
            dimensions={
                'TableName': table_name,
                'GlobalSecondaryIndexName': gsi_name
            },
            unit='Count')
    except BotoServerError as error:
        logger.error(
            'Unknown boto error. Status: "{0}". '
            'Reason: "{1}". Message: {2}'.format(
                error.status,
                error.reason,
                error.message))
        raise
