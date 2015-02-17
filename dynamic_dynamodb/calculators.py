# -*- coding: utf-8 -*-
""" General approach to calucations """
import math

from dynamic_dynamodb.log_handler import LOGGER as logger


def decrease_reads_in_percent(
        current_provisioning, percent, min_provisioned_reads, log_tag):
    """ Decrease the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :type min_provisioned_reads: int
    :param min_provisioned_reads: Configured min provisioned reads
    :type log_tag: str
    :param log_tag: Prefix for the log
    :returns: int -- New provisioning value
    """
    percent = float(percent)
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease
    min_provisioned_reads = __get_min_reads(
        current_provisioning,
        min_provisioned_reads,
        log_tag)

    if updated_provisioning < min_provisioned_reads:
        logger.info(
            '{0} - Reached provisioned reads min limit: {1:d}'.format(
                log_tag, int(min_provisioned_reads)))

        return min_provisioned_reads

    logger.debug(
        '{0} - Read provisioning will be decreased to {1:d} units'.format(
            log_tag, int(updated_provisioning)))

    return updated_provisioning


def decrease_reads_in_units(
        current_provisioning, units, min_provisioned_reads, log_tag):
    """ Decrease the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we decrease with
    :returns: int -- New provisioning value
    :type min_provisioned_reads: int
    :param min_provisioned_reads: Configured min provisioned reads
    :type log_tag: str
    :param log_tag: Prefix for the log
    """
    updated_provisioning = int(current_provisioning) - int(units)
    min_provisioned_reads = __get_min_reads(
        current_provisioning,
        min_provisioned_reads,
        log_tag)

    if updated_provisioning < min_provisioned_reads:
        logger.info(
            '{0} - Reached provisioned reads min limit: {1:d}'.format(
                log_tag,
                int(min_provisioned_reads)))

        return min_provisioned_reads

    logger.debug(
        '{0} - Read provisioning will be decreased to {1:d} units'.format(
            log_tag,
            int(updated_provisioning)))

    return updated_provisioning


def decrease_writes_in_percent(
        current_provisioning, percent, min_provisioned_writes, log_tag):
    """ Decrease the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :returns: int -- New provisioning value
    :type min_provisioned_writes: int
    :param min_provisioned_writes: Configured min provisioned writes
    :type log_tag: str
    :param log_tag: Prefix for the log
    """
    percent = float(percent)
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease
    min_provisioned_writes = __get_min_writes(
        current_provisioning,
        min_provisioned_writes,
        log_tag)

    if updated_provisioning < min_provisioned_writes:
        logger.info(
            '{0} - Reached provisioned writes min limit: {1:d}'.format(
                log_tag,
                int(min_provisioned_writes)))

        return min_provisioned_writes

    logger.debug(
        '{0} - Write provisioning will be decreased to {1:d} units'.format(
            log_tag,
            int(updated_provisioning)))

    return updated_provisioning


def decrease_writes_in_units(
        current_provisioning, units, min_provisioned_writes, log_tag):
    """ Decrease the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we decrease with
    :returns: int -- New provisioning value
    :type min_provisioned_writes: int
    :param min_provisioned_writes: Configured min provisioned writes
    :type log_tag: str
    :param log_tag: Prefix for the log
    """
    updated_provisioning = int(current_provisioning) - int(units)
    min_provisioned_writes = __get_min_writes(
        current_provisioning,
        min_provisioned_writes,
        log_tag)

    if updated_provisioning < min_provisioned_writes:
        logger.info(
            '{0} - Reached provisioned writes min limit: {1:d}'.format(
                log_tag,
                int(min_provisioned_writes)))

        return min_provisioned_writes

    logger.debug(
        '{0} - Write provisioning will be decreased to {1:d} units'.format(
            log_tag,
            int(updated_provisioning)))

    return updated_provisioning


def increase_reads_in_percent(
        current_provisioning, percent, max_provisioned_reads,
        consumed_read_units_percent, log_tag):
    """ Increase the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :type max_provisioned_reads: int
    :param max_provisioned_reads: Configured max provisioned reads
    :returns: int -- New provisioning value
    :type consumed_read_units_percent: float
    :param consumed_read_units_percent: Number of consumed read units
    :type log_tag: str
    :param log_tag: Prefix for the log
    """
    current_provisioning = float(current_provisioning)
    consumed_read_units_percent = float(consumed_read_units_percent)
    percent = float(percent)
    consumption_based_current_provisioning = \
        float(math.ceil(current_provisioning*(consumed_read_units_percent/100)))

    if consumption_based_current_provisioning > current_provisioning:
        increase = int(
            math.ceil(consumption_based_current_provisioning*(percent/100)))
        updated_provisioning = consumption_based_current_provisioning + increase
    else:
        increase = int(math.ceil(current_provisioning*(percent/100)))
        updated_provisioning = current_provisioning + increase

    if max_provisioned_reads > 0:
        if updated_provisioning > max_provisioned_reads:
            logger.info(
                '{0} - Reached provisioned reads max limit: {1}'.format(
                    log_tag,
                    max_provisioned_reads))

            return max_provisioned_reads

    logger.debug(
        '{0} - Read provisioning will be increased to {1} units'.format(
            log_tag,
            updated_provisioning))

    return updated_provisioning


def increase_reads_in_units(
        current_provisioning, units, max_provisioned_reads,
        consumed_read_units_percent, log_tag):
    """ Increase the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we increase with
    :returns: int -- New provisioning value
    :type max_provisioned_reads: int
    :param max_provisioned_reads: Configured max provisioned reads
    :returns: int -- New provisioning value
    :type consumed_read_units_percent: float
    :param consumed_read_units_percent: Number of consumed read units
    :type log_tag: str
    :param log_tag: Prefix for the log
    """
    units = int(units)
    current_provisioning = float(current_provisioning)
    consumed_read_units_percent = float(consumed_read_units_percent)
    consumption_based_current_provisioning = \
        int(math.ceil(current_provisioning*(consumed_read_units_percent/100)))

    if consumption_based_current_provisioning > current_provisioning:
        updated_provisioning = consumption_based_current_provisioning + units
    else:
        updated_provisioning = int(current_provisioning) + units

    if max_provisioned_reads > 0:
        if updated_provisioning > max_provisioned_reads:
            logger.info(
                '{0} - Reached provisioned reads max limit: {1}'.format(
                    log_tag,
                    max_provisioned_reads))

            return max_provisioned_reads

    logger.debug(
        '{0} - Read provisioning will be increased to {1:d} units'.format(
            log_tag,
            int(updated_provisioning)))

    return updated_provisioning


def increase_writes_in_percent(
        current_provisioning, percent, max_provisioned_writes,
        consumed_write_units_percent, log_tag):
    """ Increase the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :returns: int -- New provisioning value
    :type max_provisioned_writes: int
    :param max_provisioned_writes: Configured max provisioned writes
    :type consumed_write_units_percent: float
    :param consumed_write_units_percent: Number of consumed write units
    :type log_tag: str
    :param log_tag: Prefix for the log
    """
    current_provisioning = float(current_provisioning)
    consumed_write_units_percent = float(consumed_write_units_percent)
    percent = float(percent)
    consumption_based_current_provisioning = \
        int(math.ceil(current_provisioning*(consumed_write_units_percent/100)))

    if consumption_based_current_provisioning > current_provisioning:
        increase = int(
            math.ceil(consumption_based_current_provisioning*(percent/100)))
        updated_provisioning = consumption_based_current_provisioning + increase
    else:
        increase = int(math.ceil(current_provisioning*(float(percent)/100)))
        updated_provisioning = current_provisioning + increase

    if max_provisioned_writes > 0:
        if updated_provisioning > max_provisioned_writes:

            logger.info(
                '{0} - Reached provisioned writes max limit: {1}'.format(
                    log_tag,
                    max_provisioned_writes))

            return max_provisioned_writes

    logger.debug(
        '{0} - Write provisioning will be increased to {1:d} units'.format(
            log_tag,
            int(updated_provisioning)))

    return updated_provisioning


def increase_writes_in_units(
        current_provisioning, units, max_provisioned_writes,
        consumed_write_units_percent, log_tag):
    """ Increase the current_provisioning with units units

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type units: int
    :param units: How many units should we increase with
    :returns: int -- New provisioning value
    :type max_provisioned_writes: int
    :param max_provisioned_writes: Configured max provisioned writes
    :type consumed_write_units_percent: float
    :param consumed_write_units_percent: Number of consumed write units
    :type log_tag: str
    :param log_tag: Prefix for the log
    """
    units = int(units)
    current_provisioning = float(current_provisioning)
    consumed_write_units_percent = float(consumed_write_units_percent)
    consumption_based_current_provisioning = \
        int(math.ceil(current_provisioning*(consumed_write_units_percent/100)))

    if consumption_based_current_provisioning > current_provisioning:
        updated_provisioning = consumption_based_current_provisioning + units
    else:
        updated_provisioning = int(current_provisioning) + units

    if max_provisioned_writes > 0:
        if updated_provisioning > max_provisioned_writes:
            logger.info(
                '{0} - Reached provisioned writes max limit: {1}'.format(
                    log_tag,
                    max_provisioned_writes))

            return max_provisioned_writes

    logger.debug(
        '{0} - Write provisioning will be increased to {1:d} units'.format(
            log_tag,
            int(updated_provisioning)))

    return updated_provisioning


def __get_min_reads(current_provisioning, min_provisioned_reads, log_tag):
    """ Get the minimum number of reads to current_provisioning

    :type current_provisioning: int
    :param current_provisioning: Current provisioned reads
    :type min_provisioned_reads: int
    :param min_provisioned_reads: Configured min provisioned reads
    :type log_tag: str
    :param log_tag: Prefix for the log
    :returns: int -- Minimum number of reads
    """
    # Fallback value to ensure that we always have at least 1 read
    reads = 1

    if min_provisioned_reads:
        reads = int(min_provisioned_reads)

        if reads > int(current_provisioning * 2):
            reads = int(current_provisioning * 2)
            logger.debug(
                '{0} - '
                'Cannot reach min-provisioned-reads as max scale up '
                'is 100% of current provisioning'.format(log_tag))

    logger.debug(
        '{0} - Setting min provisioned reads to {1}'.format(
            log_tag, min_provisioned_reads))

    return reads


def __get_min_writes(current_provisioning, min_provisioned_writes, log_tag):
    """ Get the minimum number of writes to current_provisioning

    :type current_provisioning: int
    :param current_provisioning: Current provisioned writes
    :type min_provisioned_writes: int
    :param min_provisioned_writes: Configured min provisioned writes
    :type log_tag: str
    :param log_tag: Prefix for the log
    :returns: int -- Minimum number of writes
    """
    # Fallback value to ensure that we always have at least 1 read
    writes = 1

    if min_provisioned_writes:
        writes = int(min_provisioned_writes)

        if writes > int(current_provisioning * 2):
            writes = int(current_provisioning * 2)
            logger.debug(
                '{0} - '
                'Cannot reach min-provisioned-writes as max scale up '
                'is 100% of current provisioning'.format(log_tag))

    logger.debug(
        '{0} - Setting min provisioned writes to {1}'.format(
            log_tag, min_provisioned_writes))

    return writes
