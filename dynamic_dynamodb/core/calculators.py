""" Module with various calculators """
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import CONFIGURATION as config


def decrease_reads_in_percent(current_provisioning, percent):
    """ Decrease the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :returns: int -- New provisioning value
    """
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease

    if config['min_provisioned_reads'] > 0:
        if updated_provisioning < config['min_provisioned_reads']:
            logger.info('Reached provisioned reads min limit: {0:d}'.format(
                int(config['min_provisioned_reads'])))
            return config['min_provisioned_reads']

    return updated_provisioning


def increase_reads_in_percent(current_provisioning, percent):
    """ Increase the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :returns: int -- New provisioning value
    """
    updated_provisioning = int(
        float(current_provisioning)*(float(percent)/100+1))

    if config['max_provisioned_reads'] > 0:
        if updated_provisioning > config['max_provisioned_reads']:
            logger.info('Reached provisioned reads max limit: {0:d}'.format(
                int(config['max_provisioned_reads'])))
            return config['max_provisioned_reads']

    return updated_provisioning


def decrease_writes_in_percent(current_provisioning, percent):
    """ Decrease the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :returns: int -- New provisioning value
    """
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease

    if config['min_provisioned_writes'] > 0:
        if updated_provisioning < config['min_provisioned_writes']:
            logger.info('Reached provisioned writes min limit: {0:d}'.format(
                int(config['min_provisioned_writes'])))
            return config['min_provisioned_writes']

    return updated_provisioning


def increase_writes_in_percent(current_provisioning, percent):
    """ Increase the current_provisioning with percent %

    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :returns: int -- New provisioning value
    """
    updated_provisioning = int(
        float(current_provisioning)*(float(percent)/100+1))

    if config['max_provisioned_writes'] > 0:
        if updated_provisioning > config['max_provisioned_writes']:
            logger.info('Reached provisioned writes max limit: {0:d}'.format(
                int(config['max_provisioned_writes'])))
            return config['max_provisioned_writes']

    return updated_provisioning
