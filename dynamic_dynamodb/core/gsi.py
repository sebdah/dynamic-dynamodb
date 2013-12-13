""" Core components """
from dynamic_dynamodb.core import calculators
from dynamic_dynamodb.core import circuit_breaker
from dynamic_dynamodb.core import dynamodb
from dynamic_dynamodb.statistics import gsi as gsi_stats
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_global_option, get_table_option


def ensure_provisioning(table_name, key_name):
    """ Ensure that provisioning is correct for Global Secondary Indexes

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    """
    if get_global_option('circuit_breaker_url'):
        if circuit_breaker.is_open():
            logger.warning('Circuit breaker is OPEN!')
            return None

    gsis = dynamodb.table_gsis(table_name)

    if not gsis:
        logger.debug('{0} - No global secondary indexes found'.format(
            table_name))
        return

    gsi_names = []
    for gsi in gsis:
        gsi_names.append(gsi[u'IndexName'])

    logger.info(
        '{0} - Will ensure provisioning for the followig '
        'global secondary indexes: {1}'.format(
            table_name, ', '.join(gsi_names)))

    for gsi in gsis:
        current_ru = gsi[u'ProvisionedThroughput'][u'ReadCapacityUnits']
        current_wu = gsi[u'ProvisionedThroughput'][u'WriteCapacityUnits']
        read_update_needed, updated_read_units = __ensure_provisioning_reads(
            table_name, gsi[u'IndexName'], key_name)


def __ensure_provisioning_reads(table_name, index_name, key_name):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_name: str
    :param table_name: Name of the GSI index
    :type key_name: str
    :param key_name: Configuration option key name
    :returns: (bool, int) -- update_needed, updated_read_units
    """
    update_needed = False
    updated_read_units = statistics.get_provisioned_read_units(table_name)

    consumed_read_units_percent = statistics.get_consumed_read_units_percent(
        table_name)

    if (consumed_read_units_percent == 0 and not
            get_table_option(
                key_name, 'allow_scaling_down_reads_on_0_percent')):

        logger.info(
            '{0} - Scaling down reads is not done when usage is at 0%'.format(
                table_name))

    elif (consumed_read_units_percent >=
            get_table_option(key_name, 'reads_upper_threshold')):

        if get_table_option(key_name, 'increase_reads_unit') == 'percent':
            updated_provisioning = calculators.increase_reads_in_percent(
                updated_read_units,
                get_table_option(key_name, 'increase_reads_with'),
                key_name)
        else:
            updated_provisioning = calculators.increase_reads_in_units(
                updated_read_units,
                get_table_option(key_name, 'increase_reads_with'),
                key_name)

        if updated_read_units != updated_provisioning:
            update_needed = True
            updated_read_units = updated_provisioning

    elif (consumed_read_units_percent <=
            get_table_option(key_name, 'reads_lower_threshold')):

        if get_table_option(key_name, 'decrease_reads_unit') == 'percent':
            updated_provisioning = calculators.decrease_reads_in_percent(
                updated_read_units,
                get_table_option(key_name, 'decrease_reads_with'),
                key_name)
        else:
            updated_provisioning = calculators.decrease_reads_in_units(
                updated_read_units,
                get_table_option(key_name, 'decrease_reads_with'),
                key_name)

        if updated_read_units != updated_provisioning:
            update_needed = True
            updated_read_units = updated_provisioning

    if (int(updated_read_units) >
            int(get_table_option(key_name, 'max_provisioned_reads'))):
        update_needed = True
        updated_read_units = int(
            get_table_option(key_name, 'max_provisioned_reads'))
        logger.info(
            'Will not increase writes over max-provisioned-reads '
            'limit ({0} writes)'.format(updated_read_units))

    return update_needed, int(updated_read_units)
