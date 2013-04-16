""" Module with various calculators """
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_table_option


def decrease_reads_in_percent(table_name, current_provisioning, percent):
    """ Decrease the current_provisioning with percent %

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :returns: int -- New provisioning value
    """
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease

    if get_table_option(table_name, 'min_provisioned_writesprovisioned_reads') > 0:
        if (updated_provisioning <
            get_table_option(table_name, 'min_provisioned_reads')):

            logger.info('Reached provisioned reads min limit: {0:d}'.format(
                int(get_table_option(table_name, 'min_provisioned_reads'))))

            return get_table_option(table_name, 'min_provisioned_reads')

    return updated_provisioning


def increase_reads_in_percent(table_name, current_provisioning, percent):
    """ Increase the current_provisioning with percent %

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :returns: int -- New provisioning value
    """
    updated_provisioning = int(
        float(current_provisioning)*(float(percent)/100+1))

    if get_table_option(table_name, 'max_provisioned_reads') > 0:
        if (updated_provisioning >
            get_table_option(table_name, 'max_provisioned_reads')):

            logger.info('Reached provisioned reads max limit: {0:d}'.format(
                int(get_table_option(table_name, 'max_provisioned_reads'))))

            return get_table_option(table_name, 'max_provisioned_reads')

    return updated_provisioning


def decrease_writes_in_percent(table_name, current_provisioning, percent):
    """ Decrease the current_provisioning with percent %

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we decrease with
    :returns: int -- New provisioning value
    """
    decrease = int(float(current_provisioning)*(float(percent)/100))
    updated_provisioning = current_provisioning - decrease

    if get_table_option(table_name, 'min_provisioned_writes') > 0:
        if (updated_provisioning <
            get_table_option(table_name, 'min_provisioned_writes')):

            logger.info('Reached provisioned writes min limit: {0:d}'.format(
                int(get_table_option(table_name, 'min_provisioned_writes'))))

            return get_table_option(table_name, 'min_provisioned_writes')

    return updated_provisioning


def increase_writes_in_percent(table_name, current_provisioning, percent):
    """ Increase the current_provisioning with percent %

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type current_provisioning: int
    :param current_provisioning: The current provisioning
    :type percent: int
    :param percent: How many percent should we increase with
    :returns: int -- New provisioning value
    """
    updated_provisioning = int(
        float(current_provisioning)*(float(percent)/100+1))

    if get_table_option(table_name, 'max_provisioned_writes') > 0:
        if (updated_provisioning >
            get_table_option(table_name, 'max_provisioned_writes')):

            logger.info('Reached provisioned writes max limit: {0:d}'.format(
                int(get_table_option(table_name, 'max_provisioned_writes'))))

            return get_table_option(table_name, 'max_provisioned_writes')

    return updated_provisioning
