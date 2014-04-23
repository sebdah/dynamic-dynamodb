# -*- coding: utf-8 -*-
""" Module with various calculators """
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_table_option
from dynamic_dynamodb import calculators


def decrease_reads_in_units(current_provisioning, units, key_name, table_name):
    """ Decrease the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we decrease with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    :type table_name: str
    :param table_name: Name of the DynamoDB table
    """
    updated_provisioning = int(current_provisioning) - int(units)
    min_provisioned_reads = calculators.get_min_reads(
        current_provisioning,
        get_table_option(key_name, 'min_provisioned_reads'),
        table_name)

    if updated_provisioning < min_provisioned_reads:
        logger.info(
            '{0} - Reached provisioned reads min limit: {1:d}'.format(
                table_name,
                min_provisioned_reads))

        return min_provisioned_reads

    logger.debug(
        '{0} - Read provisioning will be decreased to {1:d} units'.format(
            table_name,
            updated_provisioning))

    return updated_provisioning


def increase_reads_in_units(current_provisioning, units, key_name, table_name):
    """ Increase the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we increase with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    :type table_name: str
    :param table_name: Name of the DynamoDB table
    """
    updated_provisioning = 0

    if int(units) > int(current_provisioning):
        updated_provisioning = 2 * int(current_provisioning)
    else:
        updated_provisioning = int(current_provisioning) + int(units)

    if get_table_option(key_name, 'max_provisioned_reads') > 0:
        if (updated_provisioning >
                get_table_option(key_name, 'max_provisioned_reads')):

            logger.info(
                '{0} - Reached provisioned reads max limit: {1:d}'.format(
                    table_name,
                    int(get_table_option(key_name, 'max_provisioned_reads'))))

            return get_table_option(key_name, 'max_provisioned_reads')

    logger.debug(
        '{0} - Read provisioning will be increased to {1:d} units'.format(
            table_name,
            updated_provisioning))

    return updated_provisioning


def decrease_writes_in_units(
        current_provisioning, units, key_name, table_name):
    """ Decrease the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we decrease with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    :type table_name: str
    :param table_name: Name of the DynamoDB table
    """
    updated_provisioning = int(current_provisioning) - int(units)
    min_provisioned_writes = calculators.get_min_writes(
        current_provisioning,
        get_table_option(key_name, 'min_provisioned_writes'),
        table_name)

    if updated_provisioning < min_provisioned_writes:
        logger.info(
            '{0} - Reached provisioned writes min limit: {1:d}'.format(
                table_name,
                min_provisioned_writes))

        return min_provisioned_writes

    logger.debug(
        '{0} - Write provisioning will be decreased to {1:d} units'.format(
            table_name,
            updated_provisioning))

    return updated_provisioning


def increase_writes_in_units(
        current_provisioning, units, key_name, table_name):
    """ Increase the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we increase with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    :type table_name: str
    :param table_name: Name of the DynamoDB table
    """
    updated_provisioning = 0
    if int(units) > int(current_provisioning):
        updated_provisioning = 2 * int(current_provisioning)
    else:
        updated_provisioning = int(current_provisioning) + int(units)

    if get_table_option(key_name, 'max_provisioned_writes') > 0:
        if (updated_provisioning >
                get_table_option(key_name, 'max_provisioned_writes')):

            logger.info(
                '{0} - Reached provisioned writes max limit: {1:d}'.format(
                    table_name,
                    int(get_table_option(key_name, 'max_provisioned_writes'))))

            return get_table_option(key_name, 'max_provisioned_writes')

    logger.debug(
        '{0} - Write provisioning will be increased to {1:d} units'.format(
            table_name,
            updated_provisioning))

    return updated_provisioning
