""" Core components """
import datetime

import dynamodb
import statistics
import calculators
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import CONFIGURATION as config

from boto.exception import DynamoDBResponseError


def ensure_provisioning(table_name):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    """
    consumed_read_units_percent = \
        statistics.get_consumed_read_units_percent(table_name)
    consumed_write_units_percent = \
        statistics.get_consumed_write_units_percent(table_name)

    updated_throughput = {
        'read_units': statistics.get_consumed_read_units(table_name),
        'write_units': statistics.get_consumed_write_units(table_name),
        'update_needed': False
    }

    if (consumed_read_units_percent == 0 and not
        config['allow_scaling_down_reads_on_0_percent']):
        logger.info('Scaling down reads is not done when usage is at 0%')

    elif consumed_read_units_percent >= config['reads_upper_threshold']:
        updated_provisioning = calculators.increase_reads_in_percent(
            updated_throughput['read_units'],
            config['increase_reads_with'])
        updated_throughput['update_needed'] = True
        updated_throughput['read_units'] = updated_provisioning

    elif consumed_read_units_percent <= config['reads_lower_threshold']:
        updated_provisioning = calculators.decrease_reads_in_percent(
            updated_throughput['read_units'],
            config['decrease_reads_with'])
        updated_throughput['update_needed'] = True
        updated_throughput['read_units'] = updated_provisioning

    # Check if we should update write provisioning
    if (consumed_write_units_percent == 0 and not
        config['allow_scaling_down_writes_on_0_percent']):
        logger.info('Scaling down writes is not done when usage is at 0%')

    elif consumed_write_units_percent >= config['writes_upper_threshold']:
        updated_provisioning = calculators.increase_writes_in_percent(
            updated_throughput['write_units'],
            config['increase_writes_with'])
        updated_throughput['update_needed'] = True
        updated_throughput['write_units'] = updated_provisioning

    elif consumed_write_units_percent <= config['writes_lower_threshold']:
        updated_provisioning = calculators.decrease_writes_in_percent(
            updated_throughput['write_units'],
            config['decrease_writes_with'])
        updated_throughput['update_needed'] = True
        updated_throughput['write_units'] = updated_provisioning

    # Handle throughput updates
    if updated_throughput['update_needed']:
        logger.info(
            'Changing provisioning to {0:d} reads and {1:d} writes'.format(
                int(updated_throughput['read_units']),
                int(updated_throughput['write_units'])))
        update_throughput(
            table_name,
            updated_throughput['read_units'],
            updated_throughput['write_units'])
    else:
        logger.info('No need to change provisioning')


def is_maintenance_window(maintenance_windows):
    """ Checks that the current time is within the maintenance window

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
            logger.error('Malformatted maintenance window')
            return False

        maintenance_window_list.append((start, end))

    now = datetime.datetime.utcnow().strftime('%H%M')
    for maintenance_window in maintenance_window_list:
        start = ''.join(maintenance_window[0].split(':'))
        end = ''.join(maintenance_window[1].split(':'))
        if now >= start and now <= end:
            return True

    return False


def update_throughput(table_name, read_units, write_units):
    """ Update throughput on the DynamoDB table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type read_units: int
    :param read_units: New read unit provisioning
    :type write_units: int
    :param write_units: New write unit provisioning
    """
    table = dynamodb.get_table(table_name)

    # Check that we are in the right time frame
    if config['maintenance_windows']:
        if not is_maintenance_window(config['maintenance_windows']):
            logger.warning('Current time is outside maintenance window')
            return
        else:
            logger.info('Current time is within maintenance window')

    # Check table status
    if table.status != 'ACTIVE':
        logger.warning(
            'Not performing throughput changes when table '
            'is in {0} state'.format(table.status))

    # If this setting is True, we will only scale down when
    # BOTH reads AND writes are low
    if config['always_decrease_rw_together']:
        if read_units < table.read_units and write_units < table.write_units:
            logger.info('Both reads and writes will be decreased')
        elif read_units < table.read_units:
            logger.info(
                'Will not decrease reads nor writes, '
                'waiting for both to become low before decrease')
            read_units = table.read_units
        elif write_units < table.write_units:
            logger.info(
                'Will not decrease reads nor writes, '
                'waiting for both to become low before decrease')
            write_units = table.write_units

    if not config['dry_run']:
        try:
            table.update_throughput(int(read_units), int(write_units))
            logger.info('Provisioning updated')
        except DynamoDBResponseError as error:
            dynamodb_error = error.body['__type'].rsplit('#', 1)[1]
            if dynamodb_error == 'LimitExceededException':
                logger.warning(
                    'Scaling limit exeeded. '
                    'The table can only be scaled down twice per day.')

                if int(read_units) > table.read_units:
                    logger.info('Scaling up reads to {0:d}'.format(
                        int(read_units)))
                    update_throughput(
                        table_name,
                        int(read_units),
                        int(table.write_units))

                elif int(write_units) > table.write_units:
                    logger.info('Scaling up writes to {0:d}'.format(
                        int(write_units)))
                    update_throughput(
                        table_name,
                        int(table.read_units),
                        int(write_units))

            elif dynamodb_error == 'ValidationException':
                logger.warning('ValidationException: {0}'.format(
                    error.body['message']))

            else:
                logger.error(
                    (
                        'Unhandled exception: {0}: {1}. '
                        'Please file a bug report at {3}'
                    ).format(
                    dynamodb_error,
                    error.body['message'],
                    'https://github.com/sebdah/dynamic-dynamodb/issues'))
