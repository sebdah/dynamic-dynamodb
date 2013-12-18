""" Core components """
import datetime

from dynamic_dynamodb.calculators import table as calculators
from dynamic_dynamodb.core import circuit_breaker
from dynamic_dynamodb.core import dynamodb
from dynamic_dynamodb.statistics import table as table_stats
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_table_option, get_global_option

from boto.exception import DynamoDBResponseError


def ensure_provisioning(table_name, key_name):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    """
    if get_global_option('circuit_breaker_url'):
        if circuit_breaker.is_open():
            logger.warning('Circuit breaker is OPEN!')
            return None

    read_update_needed, updated_read_units = __ensure_provisioning_reads(
        table_name, key_name)
    write_update_needed, updated_write_units = __ensure_provisioning_writes(
        table_name, key_name)

    # Handle throughput updates
    if read_update_needed or write_update_needed:
        logger.info(
            '{0} - Changing provisioning to {1:d} '
            'read units and {2:d} write units'.format(
                table_name,
                int(updated_read_units),
                int(updated_write_units)))
        __update_throughput(
            table_name, updated_read_units, updated_write_units, key_name)
    else:
        logger.info('{0} - No need to change provisioning'.format(table_name))


def __ensure_provisioning_reads(table_name, key_name):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    :returns: (bool, int) -- update_needed, updated_read_units
    """
    update_needed = False
    updated_read_units = table_stats.get_provisioned_read_units(table_name)

    consumed_read_units_percent = table_stats.get_consumed_read_units_percent(
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
                key_name,
                table_name)
        else:
            updated_provisioning = calculators.increase_reads_in_units(
                updated_read_units,
                get_table_option(key_name, 'increase_reads_with'),
                key_name,
                table_name)

        if updated_read_units != updated_provisioning:
            update_needed = True
            updated_read_units = updated_provisioning

    elif (consumed_read_units_percent <=
            get_table_option(key_name, 'reads_lower_threshold')):

        if get_table_option(key_name, 'decrease_reads_unit') == 'percent':
            updated_provisioning = calculators.decrease_reads_in_percent(
                updated_read_units,
                get_table_option(key_name, 'decrease_reads_with'),
                key_name,
                table_name)
        else:
            updated_provisioning = calculators.decrease_reads_in_units(
                updated_read_units,
                get_table_option(key_name, 'decrease_reads_with'),
                key_name,
                table_name)

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


def __ensure_provisioning_writes(table_name, key_name):
    """ Ensure that provisioning of writes is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    :returns: (bool, int) -- update_needed, updated_write_units
    """
    update_needed = False
    updated_write_units = table_stats.get_provisioned_write_units(table_name)

    consumed_write_units_percent = \
        table_stats.get_consumed_write_units_percent(table_name)

    # Check if we should update write provisioning
    if (consumed_write_units_percent == 0 and not
            get_table_option(
                key_name, 'allow_scaling_down_writes_on_0_percent')):

        logger.info(
            '{0} - Scaling down writes is not done when usage is at 0%'.format(
                table_name))

    elif (consumed_write_units_percent >=
            get_table_option(key_name, 'writes_upper_threshold')):

        if get_table_option(key_name, 'increase_writes_unit') == 'percent':
            updated_provisioning = calculators.increase_writes_in_percent(
                updated_write_units,
                get_table_option(key_name, 'increase_writes_with'),
                key_name,
                table_name)
        else:
            updated_provisioning = calculators.increase_writes_in_units(
                updated_write_units,
                get_table_option(key_name, 'increase_writes_with'),
                key_name,
                table_name)

        if updated_write_units != updated_provisioning:
            update_needed = True
            updated_write_units = updated_provisioning

    elif (consumed_write_units_percent <=
            get_table_option(key_name, 'writes_lower_threshold')):

        if get_table_option(key_name, 'decrease_writes_unit') == 'percent':
            updated_provisioning = calculators.decrease_writes_in_percent(
                updated_write_units,
                get_table_option(key_name, 'decrease_writes_with'),
                key_name,
                table_name)
        else:
            updated_provisioning = calculators.decrease_writes_in_units(
                updated_write_units,
                get_table_option(key_name, 'decrease_writes_with'),
                key_name,
                table_name)

        if updated_write_units != updated_provisioning:
            update_needed = True
            updated_write_units = updated_provisioning

    if (int(updated_write_units) >
            int(get_table_option(key_name, 'max_provisioned_writes'))):
        update_needed = True
        updated_write_units = int(
            get_table_option(key_name, 'max_provisioned_writes'))
        logger.info(
            'Will not increase writes over max-provisioned-writes '
            'limit ({0} writes)'.format(updated_write_units))

    return update_needed, int(updated_write_units)


def __is_maintenance_window(table_name, maintenance_windows):
    """ Checks that the current time is within the maintenance window

    :type table_name: str
    :param table_name: Name of the DynamoDB table
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
                '{0} - Malformatted maintenance window'.format(table_name))
            return False

        maintenance_window_list.append((start, end))

    now = datetime.datetime.utcnow().strftime('%H%M')
    for maintenance_window in maintenance_window_list:
        start = ''.join(maintenance_window[0].split(':'))
        end = ''.join(maintenance_window[1].split(':'))
        if now >= start and now <= end:
            return True

    return False


def __update_throughput(table_name, read_units, write_units, key_name):
    """ Update throughput on the DynamoDB table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type read_units: int
    :param read_units: New read unit provisioning
    :type write_units: int
    :param write_units: New write unit provisioning
    :type key_name: str
    :param key_name: Configuration option key name
    """
    try:
        table = dynamodb.get_table(table_name)
    except DynamoDBResponseError:
        # Return if the table does not exist
        return None

    # Check that we are in the right time frame
    if get_table_option(key_name, 'maintenance_windows'):
        if (not __is_maintenance_window(table_name, get_table_option(
                key_name, 'maintenance_windows'))):

            logger.warning(
                '{0} - Current time is outside maintenance window'.format(
                    table_name))
            return
        else:
            logger.info(
                '{0} - Current time is within maintenance window'.format(
                    table_name))

    # Check table status
    table_status = dynamodb.get_table_status(table_name)
    if table_status != 'ACTIVE':
        logger.warning(
            '{0} - Not performing throughput changes when table '
            'is in {1} state'.format(table_name, table_status))
        return

    # If this setting is True, we will only scale down when
    # BOTH reads AND writes are low
    if get_table_option(key_name, 'always_decrease_rw_together'):
        if ((read_units < table.throughput['read']) or
                (table.throughput['read'] == get_table_option(
                    key_name, 'min_provisioned_reads'))):
            if ((write_units < table.throughput['write']) or
                    (table.throughput['write'] == get_table_option(
                        key_name, 'min_provisioned_writes'))):
                logger.info(
                    '{0} - Both reads and writes will be decreased'.format(
                        table_name))

        elif read_units < table.throughput['read']:
            logger.info(
                '{0} - Will not decrease reads nor writes, waiting for '
                'both to become low before decrease'.format(table_name))
            read_units = table.throughput['read']
        elif write_units < table.throughput['write']:
            logger.info(
                '{0} - Will not decrease reads nor writes, waiting for '
                'both to become low before decrease'.format(table_name))
            write_units = table.throughput['write']

    if not get_global_option('dry_run'):
        try:
            table.update(
                throughput={
                    'read': int(read_units),
                    'write': int(write_units)
                })
            logger.info(
                '{0} - Provisioning updated '
                'to {1} reads and {2} writes'.format(
                    table_name, read_units, write_units))
        except DynamoDBResponseError as error:
            dynamodb_error = error.body['__type'].rsplit('#', 1)[1]
            if dynamodb_error == 'LimitExceededException':
                logger.warning(
                    '{0} - {1}'.format(table_name, error.body['message']))

                if int(read_units) > table.throughput['read']:
                    logger.info('{0} - Scaling up reads to {1:d}'.format(
                        table_name,
                        int(read_units)))
                    __update_throughput(
                        table_name,
                        int(read_units),
                        int(table.throughput['write']),
                        key_name)

                elif int(write_units) > table.throughput['write']:
                    logger.info('{0} - Scaling up writes to {1:d}'.format(
                        table_name,
                        int(write_units)))
                    __update_throughput(
                        table_name,
                        int(table.throughput['read']),
                        int(write_units),
                        key_name)

            elif dynamodb_error == 'ValidationException':
                logger.warning('{0} - ValidationException: {1}'.format(
                    table_name,
                    error.body['message']))

            elif dynamodb_error == 'ResourceInUseException':
                logger.warning('{0} - ResourceInUseException: {1}'.format(
                    table_name,
                    error.body['message']))

            elif dynamodb_error == 'AccessDeniedException':
                logger.warning('{0} - AccessDeniedException: {1}'.format(
                    table_name,
                    error.body['message']))

            else:
                logger.error(
                    (
                        '{0} - Unhandled exception: {1}: {2}. '
                        'Please file a bug report at '
                        'https://github.com/sebdah/dynamic-dynamodb/issues'
                    ).format(
                        table_name,
                        dynamodb_error,
                        error.body['message']))