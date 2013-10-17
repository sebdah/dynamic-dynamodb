""" Module with various calculators """
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_table_option


def get_min_provisioned_reads(current_provisioning, key_name):
    """ Returns the minimum provisioned reads

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type key_name: str
    :param key_name: Name of the key
    :returns: int -- Minimum provisioned reads
    """
    if get_table_option(key_name, 'min_provisioned_reads'):
        return int(min(
            get_table_option(key_name, 'min_provisioned_reads'),
            (current_provisioning * 2)))

    return int(current_provisioning * 2)


def get_min_provisioned_writes(current_provisioning, key_name):
    """ Returns the minimum provisioned writes

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :returns: int -- Minimum provisioned writes
    :type key_name: str
    :param key_name: Name of the key
    """
    if get_table_option(key_name, 'min_provisioned_writes'):
        return int(min(
            get_table_option(key_name, 'min_provisioned_writes'),
            (current_provisioning * 2)))

    return int(current_provisioning * 2)


def decrease_reads_in_percent(current_provisioning, percent, key_name):
    """ Decrease the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :type key_name: str
    :param key_name: Name of the key
    :returns: int -- New provisioning value
    """
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease
    logger.debug(
        'Read provisioning will be decreased to {0:d} units'.format(
            updated_provisioning))

    min_provisioned_reads = get_min_provisioned_reads(
        current_provisioning,
        key_name)

    if min_provisioned_reads > 0:
        if updated_provisioning < min_provisioned_reads:
            logger.info('Reached provisioned reads min limit: {0:d}'.format(
                min_provisioned_reads))

            return min_provisioned_reads

    return updated_provisioning


def increase_reads_in_percent(current_provisioning, percent, key_name):
    """ Increase the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    """
    increase = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning + increase
    logger.debug(
        'Read provisioning will be increased to {0:d} units'.format(
            updated_provisioning))

    if get_table_option(key_name, 'max_provisioned_reads') > 0:
        if (updated_provisioning >
                get_table_option(key_name, 'max_provisioned_reads')):

            logger.info('Reached provisioned reads max limit: {0:d}'.format(
                int(get_table_option(key_name, 'max_provisioned_reads'))))

            return get_table_option(key_name, 'max_provisioned_reads')

    return updated_provisioning


def decrease_writes_in_percent(current_provisioning, percent, key_name):
    """ Decrease the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    """
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease
    logger.debug(
        'Write provisioning will be decreased to {0:d} units'.format(
            updated_provisioning))

    min_provisioned_writes = get_min_provisioned_writes(
        current_provisioning,
        key_name)

    if min_provisioned_writes > 0:
        if updated_provisioning < min_provisioned_writes:
            logger.info('Reached provisioned writes min limit: {0:d}'.format(
                min_provisioned_writes))

            return min_provisioned_writes

    return updated_provisioning


def increase_writes_in_percent(current_provisioning, percent, key_name):
    """ Increase the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    """
    increase = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning + increase
    logger.debug(
        'Write provisioning will be increased to {0:d} units'.format(
            updated_provisioning))

    if get_table_option(key_name, 'max_provisioned_writes') > 0:
        if (updated_provisioning >
                get_table_option(key_name, 'max_provisioned_writes')):

            logger.info('Reached provisioned writes max limit: {0:d}'.format(
                int(get_table_option(key_name, 'max_provisioned_writes'))))

            return get_table_option(key_name, 'max_provisioned_writes')

    return updated_provisioning


def decrease_reads_in_units(current_provisioning, units, key_name):
    """ Decrease the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we decrease with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    """
    updated_provisioning = int(current_provisioning) - int(units)
    logger.debug(
        'Read provisioning will be decreased to {0:d} units'.format(
            updated_provisioning))

    min_provisioned_reads = get_min_provisioned_reads(
        current_provisioning,
        key_name)

    if min_provisioned_reads > 0:
        if updated_provisioning < min_provisioned_reads:
            logger.info('Reached provisioned reads min limit: {0:d}'.format(
                min_provisioned_reads))

            return min_provisioned_reads

    return updated_provisioning


def increase_reads_in_units(current_provisioning, units, key_name):
    """ Increase the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we increase with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    """
    updated_provisioning = 0
    if int(units) > int(current_provisioning):
        updated_provisioning = 2 * int(current_provisioning)
    else:
        updated_provisioning = int(current_provisioning) + int(units)

    logger.debug(
        'Read provisioning will be increased to {0:d} units'.format(
            updated_provisioning))

    if get_table_option(key_name, 'max_provisioned_reads') > 0:
        if (updated_provisioning >
                get_table_option(key_name, 'max_provisioned_reads')):

            logger.info('Reached provisioned reads max limit: {0:d}'.format(
                int(get_table_option(key_name, 'max_provisioned_reads'))))

            return get_table_option(key_name, 'max_provisioned_reads')

    return updated_provisioning


def decrease_writes_in_units(current_provisioning, units, key_name):
    """ Decrease the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we decrease with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    """
    updated_provisioning = int(current_provisioning) - int(units)
    logger.debug(
        'Write provisioning will be decreased to {0:d} units'.format(
            updated_provisioning))

    min_provisioned_writes = get_min_provisioned_writes(
        current_provisioning,
        key_name)

    if min_provisioned_writes > 0:
        if updated_provisioning < min_provisioned_writes:
            logger.info('Reached provisioned writes min limit: {0:d}'.format(
                min_provisioned_writes))

            return min_provisioned_writes

    return updated_provisioning


def increase_writes_in_units(current_provisioning, units, key_name):
    """ Increase the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we increase with
    :returns: int -- New provisioning value
    :type key_name: str
    :param key_name: Name of the key
    """
    updated_provisioning = 0
    if int(units) > int(current_provisioning):
        updated_provisioning = 2 * int(current_provisioning)
    else:
        updated_provisioning = int(current_provisioning) + int(units)

    logger.debug(
        'Write provisioning will be increased to {0:d} units'.format(
            updated_provisioning))

    if get_table_option(key_name, 'max_provisioned_writes') > 0:
        if (updated_provisioning >
                get_table_option(key_name, 'max_provisioned_writes')):

            logger.info('Reached provisioned writes max limit: {0:d}'.format(
                int(get_table_option(key_name, 'max_provisioned_writes'))))

            return get_table_option(key_name, 'max_provisioned_writes')

    return updated_provisioning
