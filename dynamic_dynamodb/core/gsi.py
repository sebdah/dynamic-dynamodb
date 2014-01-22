""" Core components """
import datetime

from dynamic_dynamodb.calculators import gsi as calculators
from dynamic_dynamodb.core import circuit_breaker
from dynamic_dynamodb.core import dynamodb
from dynamic_dynamodb.statistics import gsi as gsi_stats
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_global_option, get_gsi_option


def ensure_provisioning(table_name, table_key, gsi_name, gsi_key):
    """ Ensure that provisioning is correct for Global Secondary Indexes

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type gsi_key: str
    :param gsi_key: GSI configuration option key name
    """
    if get_global_option('circuit_breaker_url'):
        if circuit_breaker.is_open():
            logger.warning('Circuit breaker is OPEN!')
            return None

    logger.info(
        '{0} - Will ensure provisioning for global secondary index {1}'.format(
            table_name, gsi_name))

    read_update_needed, updated_read_units = __ensure_provisioning_reads(
        table_name,
        table_key,
        gsi_name,
        gsi_key)
    write_update_needed, updated_write_units = __ensure_provisioning_writes(
        table_name,
        table_key,
        gsi_name,
        gsi_key)

    # Handle throughput updates
    if read_update_needed or write_update_needed:
        logger.info(
            '{0} - GSI: {1} - Changing provisioning to {2:d} '
            'read units and {3:d} write units'.format(
                table_name,
                gsi_name,
                int(updated_read_units),
                int(updated_write_units)))
        __update_throughput(
            table_name,
            table_key,
            gsi_name,
            gsi_key,
            updated_read_units,
            updated_write_units)
    else:
        logger.info(
            '{0} - GSI: {1} - No need to change provisioning'.format(
                table_name,
                gsi_name))


def __ensure_provisioning_reads(table_name, table_key, gsi_name, gsi_key):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type gsi_key: str
    :param gsi_key: Configuration option key name
    :returns: (bool, int) -- update_needed, updated_read_units
    """
    update_needed = False
    updated_read_units = dynamodb.get_provisioned_gsi_read_units(
        table_name, gsi_name)

    consumed_read_units_percent = gsi_stats.get_consumed_read_units_percent(
        table_name, gsi_name)

    if (consumed_read_units_percent == 0 and not
            get_gsi_option(
                table_key,
                gsi_key,
                'allow_scaling_down_reads_on_0_percent')):

        logger.info(
            '{0} - GSI: {1} - '
            'Scaling down reads is not done when usage is at 0%'.format(
                table_name, gsi_name))

    elif (consumed_read_units_percent >=
            get_gsi_option(table_key, gsi_key, 'reads_upper_threshold')):

        if (get_gsi_option(table_key, gsi_key, 'increase_reads_unit') ==
                'percent'):
            updated_provisioning = calculators.increase_reads_in_percent(
                updated_read_units,
                get_gsi_option(table_key, gsi_key, 'increase_reads_with'),
                table_name,
                table_key,
                gsi_name,
                gsi_key,)
        else:
            updated_provisioning = calculators.increase_reads_in_units(
                updated_read_units,
                get_gsi_option(table_key, gsi_key, 'increase_reads_with'),
                table_name,
                table_key,
                gsi_name,
                gsi_key)

        if updated_read_units != updated_provisioning:
            update_needed = True
            updated_read_units = updated_provisioning

    elif (consumed_read_units_percent <=
            get_gsi_option(table_key, gsi_key, 'reads_lower_threshold')):

        if (get_gsi_option(table_key, gsi_key, 'decrease_reads_unit') ==
                'percent'):
            updated_provisioning = calculators.decrease_reads_in_percent(
                updated_read_units,
                get_gsi_option(table_key, gsi_key, 'decrease_reads_with'),
                table_name,
                table_key,
                gsi_name,
                gsi_key)
        else:
            updated_provisioning = calculators.decrease_reads_in_units(
                updated_read_units,
                get_gsi_option(table_key, gsi_key, 'decrease_reads_with'),
                table_name,
                table_key,
                gsi_name,
                gsi_key)

        if updated_read_units != updated_provisioning:
            update_needed = True
            updated_read_units = updated_provisioning

    if get_gsi_option(table_key, gsi_key, 'max_provisioned_reads'):
        if (int(updated_read_units) > int(
                get_gsi_option(table_key, gsi_key, 'max_provisioned_reads'))):
            update_needed = True
            updated_read_units = int(
                get_gsi_option(table_key, gsi_key, 'max_provisioned_reads'))
            logger.info(
                'Will not increase writes over gsi-max-provisioned-reads '
                'limit ({0} writes)'.format(updated_read_units))

    return update_needed, int(updated_read_units)


def __ensure_provisioning_writes(table_name, table_key, gsi_name, gsi_key):
    """ Ensure that provisioning of writes is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type gsi_key: str
    :param gsi_key: Configuration option key name
    :returns: (bool, int) -- update_needed, updated_write_units
    """
    update_needed = False
    updated_write_units = dynamodb.get_provisioned_gsi_write_units(
        table_name, gsi_name)

    consumed_write_units_percent = \
        gsi_stats.get_consumed_write_units_percent(table_name, gsi_name)

    # Check if we should update write provisioning
    if (consumed_write_units_percent == 0 and not get_gsi_option(
            table_key, gsi_key, 'allow_scaling_down_writes_on_0_percent')):

        logger.info(
            '{0} - GSI: {1} - '
            'Scaling down writes is not done when usage is at 0%'.format(
                table_name, gsi_name))

    elif (consumed_write_units_percent >=
            get_gsi_option(table_key, gsi_key, 'writes_upper_threshold')):

        if (get_gsi_option(table_key, gsi_key, 'increase_writes_unit') ==
                'percent'):
            updated_provisioning = calculators.increase_writes_in_percent(
                updated_write_units,
                get_gsi_option(table_key, gsi_key, 'increase_writes_with'),
                table_name,
                table_key,
                gsi_name,
                gsi_key)
        else:
            updated_provisioning = calculators.increase_writes_in_units(
                updated_write_units,
                get_gsi_option(table_key, gsi_key, 'increase_writes_with'),
                table_name,
                table_key,
                gsi_name,
                gsi_key)

        if updated_write_units != updated_provisioning:
            update_needed = True
            updated_write_units = updated_provisioning

    elif (consumed_write_units_percent <=
            get_gsi_option(table_key, gsi_key, 'writes_lower_threshold')):

        if (get_gsi_option(table_key, gsi_key, 'decrease_writes_unit') ==
                'percent'):
            updated_provisioning = calculators.decrease_writes_in_percent(
                updated_write_units,
                get_gsi_option(table_key, gsi_key, 'decrease_writes_with'),
                table_name,
                table_key,
                gsi_name,
                gsi_key)
        else:
            updated_provisioning = calculators.decrease_writes_in_units(
                updated_write_units,
                get_gsi_option(table_key, gsi_key, 'decrease_writes_with'),
                table_name,
                table_key,
                gsi_name,
                gsi_key)

        if updated_write_units != updated_provisioning:
            update_needed = True
            updated_write_units = updated_provisioning

    if get_gsi_option(table_key, gsi_key, 'max_provisioned_writes'):
        if (int(updated_write_units) > int(get_gsi_option(
                table_key, gsi_key, 'max_provisioned_writes'))):
            update_needed = True
            updated_write_units = int(get_gsi_option(
                table_key, gsi_key, 'max_provisioned_writes'))
            logger.info(
                '{0} - GSI: {1} - '
                'Will not increase writes over gsi-max-provisioned-writes '
                'limit ({2} writes)'.format(
                    table_name,
                    gsi_name,
                    updated_write_units))

    return update_needed, int(updated_write_units)


def __is_maintenance_window(table_name, gsi_name, maintenance_windows):
    """ Checks that the current time is within the maintenance window

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type maintenance_windows: str
    :param maintenance_windows: Example: '00:00-01:00,10:00-11:00'
    :returns: bool -- True if within maintenance window
    """
    # Example string '00:00-01:00,10:00-11:00'
    maintenance_window_list = []
    for window in maintenance_windows.split(','):
        try:
            start, end = window.split('-', 1)
        except ValueError:
            logger.error(
                '{0} - GSI: {1} - '
                'Malformatted maintenance window'.format(table_name))
            return False

        maintenance_window_list.append((start, end))

    now = datetime.datetime.utcnow().strftime('%H%M')
    for maintenance_window in maintenance_window_list:
        start = ''.join(maintenance_window[0].split(':'))
        end = ''.join(maintenance_window[1].split(':'))
        if now >= start and now <= end:
            return True

    return False


def __update_throughput(
        table_name, table_key, gsi_name, gsi_key, read_units, write_units):
    """ Update throughput on the GSI

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type gsi_key: str
    :param gsi_key: Configuration option key name
    :type read_units: int
    :param read_units: New read unit provisioning
    :type write_units: int
    :param write_units: New write unit provisioning
    """
    current_ru = dynamodb.get_provisioned_gsi_read_units(
        table_name, gsi_name)
    current_wu = dynamodb.get_provisioned_gsi_write_units(
        table_name, gsi_name)

    # Check that we are in the right time frame
    if get_gsi_option(table_key, gsi_key, 'maintenance_windows'):
        if (not __is_maintenance_window(table_name, gsi_name, get_gsi_option(
                table_key, gsi_key, 'maintenance_windows'))):

            logger.warning(
                '{0} - GSI: {1} - '
                'Current time is outside maintenance window'.format(
                    table_name,
                    gsi_name))
            return
        else:
            logger.info(
                '{0} - GSI: {1} - '
                'Current time is within maintenance window'.format(
                    table_name,
                    gsi_name))

    # Check table status
    gsi_status = dynamodb.get_gsi_status(table_name, gsi_name)
    logger.debug('{0} - GSI: {1} - GSI status is {2}'.format(
        table_name, gsi_name, gsi_status))
    if gsi_status != 'ACTIVE':
        logger.warning(
            '{0} - GSI: {1} - Not performing throughput changes when GSI '
            'status is {2}'.format(table_name, gsi_name, gsi_status))
        return

    # If this setting is True, we will only scale down when
    # BOTH reads AND writes are low
    if get_gsi_option(table_key, gsi_key, 'always_decrease_rw_together'):
        if read_units < current_ru and write_units < current_wu:
            logger.debug(
                '{0} - GSI: {1} - '
                'Both reads and writes will be decreased'.format(
                    table_name,
                    gsi_name))
        elif read_units < current_ru:
            logger.info(
                '{0} - GSI: {1} - '
                'Will not decrease reads nor writes, waiting for '
                'both to become low before decrease'.format(
                    table_name, gsi_name))
            return
        elif write_units < current_wu:
            logger.info(
                '{0} - GSI: {1} - '
                'Will not decrease reads nor writes, waiting for '
                'both to become low before decrease'.format(
                    table_name, gsi_name))
            return

    if not get_global_option('dry_run'):
        dynamodb.update_gsi_provisioning(
            table_name,
            gsi_name,
            int(read_units),
            int(write_units))
        logger.info(
            '{0} - GSI: {1} - '
            'Provisioning updated to {2} reads and {3} writes'.format(
                table_name,
                gsi_name,
                read_units,
                write_units))
