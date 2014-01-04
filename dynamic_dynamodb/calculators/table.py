""" Module with various calculators """
import math

from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_table_option


def get_min_provisioned_reads(current_provisioning, table_name, key_name):
    """ Returns the minimum provisioned reads

    If the min_provisioned_reads value is less than current_provisioning * 2,
    then we return current_provisioning * 2, as DynamoDB cannot be scaled up
    with more than 100%.

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type table_name: str
    :param table_name: Name of the table
    :type key_name: str
    :param key_name: Name of the key
    :returns: int -- Minimum provisioned reads
    """
    min_provisioned_reads = 1

    if get_table_option(key_name, 'min_provisioned_reads'):
        min_provisioned_reads = int(
            get_table_option(key_name, 'min_provisioned_reads'))

        if min_provisioned_reads > int(current_provisioning * 2):
            min_provisioned_reads = int(current_provisioning * 2)
            logger.debug(
                '{0} - '
                'Cannot reach min_provisioned_reads as max scale up '
                'is 100% of current provisioning'.format(
                    table_name))

    logger.debug(
        '{0} - '
        'Setting min provisioned reads to {1}'.format(
            table_name, min_provisioned_reads))

    return min_provisioned_reads


def get_min_provisioned_writes(current_provisioning, table_name, key_name):
    """ Returns the minimum provisioned writes

    If the min_provisioned_writes value is less than current_provisioning * 2,
    then we return current_provisioning * 2, as DynamoDB cannot be scaled up
    with more than 100%.

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type table_name: str
    :param table_name: Name of the table
    :type key_name: str
    :param key_name: Name of the key
    :returns: int -- Minimum provisioned writes
    """
    min_provisioned_writes = 1

    if get_table_option(key_name, 'min_provisioned_writes'):
        min_provisioned_writes = int(
            get_table_option(key_name, 'min_provisioned_writes'))

        if min_provisioned_writes > int(current_provisioning * 2):
            min_provisioned_writes = int(current_provisioning * 2)
            logger.debug(
                '{0} - '
                'Cannot reach min_provisioned_writes as max scale up '
                'is 100% of current provisioning'.format(
                    table_name))

    logger.debug(
        '{0} - '
        'Setting min provisioned writes to {1}'.format(
            table_name, min_provisioned_writes))

    return min_provisioned_writes


def decrease_reads_in_percent(
        current_provisioning, percent, key_name, table_name):
    """ Decrease the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :type key_name: str
    :param key_name: Name of the key
    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: int -- New provisioning value
    """
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease
    min_provisioned_reads = get_min_provisioned_reads(
        current_provisioning,
        table_name,
        key_name)

    if updated_provisioning < min_provisioned_reads:
        logger.info(
            '{0} - Reached provisioned reads min limit: {1:d}'.format(
                table_name, min_provisioned_reads))

        return min_provisioned_reads

    logger.debug(
        '{0} - Read provisioning will be decreased to {1:d} units'.format(
            table_name, updated_provisioning))

    return updated_provisioning


def increase_reads_in_percent(
        current_provisioning, percent, key_name, table_name):
    """ Increase the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    :type table_name: str
    :param table_name: Name of the DynamoDB table
    """
    increase = int(math.ceil(float(current_provisioning)*(float(percent)/100)))
    updated_provisioning = current_provisioning + increase

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


def decrease_writes_in_percent(
        current_provisioning, percent, key_name, table_name):
    """ Decrease the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    :type table_name: str
    :param table_name: Name of the DynamoDB table
    """
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease
    min_provisioned_writes = get_min_provisioned_writes(
        current_provisioning,
        table_name,
        key_name)

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


def increase_writes_in_percent(
        current_provisioning, percent, key_name, table_name):
    """ Increase the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    :type table_name: str
    :param table_name: Name of the DynamoDB table
    """
    increase = int(math.ceil(float(current_provisioning)*(float(percent)/100)))
    updated_provisioning = current_provisioning + increase

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
    min_provisioned_reads = get_min_provisioned_reads(
        current_provisioning,
        table_name,
        key_name)

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
    min_provisioned_writes = get_min_provisioned_writes(
        current_provisioning,
        table_name,
        key_name)

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
