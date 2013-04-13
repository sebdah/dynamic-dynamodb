""" Core components """
import statistics
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import CONFIGURATION as configuration


def ensure_provisioning(table_name):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    """
    consumed_read_units_percent = statistics.get_consumed_read_units_percent(table_name)
    consumed_write_units_percent = statistics.get_consumed_write_units_percent(table_name)

    updated_throughput = {
        'read_units': statistics.get_consumed_read_units(table_name),
        'write_units': statistics.get_consumed_write_units(table_name)
    }

    if (consumed_read_units_percent == 0 and not
        configuration['allow_scaling_down_reads_on_0_percent']):
        logger.info('Scaling down reads is not done when usage is at 0%')

    elif consumed_read_units_percent >= configuration['reads_upper_threshold']:
        new_value = self._calculate_increase_reads(
            updated_throughput['read_units'],
            configuration['increase_reads_with'])
        updated_throughput['update_needed'] = True
        updated_throughput['read_units'] = new_value

    elif consumed_read_units_percent <= configuration['reads_lower_threshold']:
        new_value = self._calculate_decrease_reads(
            updated_throughput['read_units'],
            configuration['decrease_reads_with'])
        updated_throughput['update_needed'] = True
        updated_throughput['read_units'] = new_value

    # Check if we should update write provisioning
    if (consumed_write_units_percent == 0 and not
        configuration['allow_scaling_down_writes_on_0_percent']):
        logger.info('Scaling down writes is not done when usage is at 0%')

    elif consumed_write_units_percent >= configuration['writes_upper_threshold']:
        new_value = self._calculate_increase_writes(
            updated_throughput['write_units'],
            configuration['increase_writes_with'])
        updated_throughput['update_needed'] = True
        updated_throughput['write_units'] = new_value

    elif consumed_write_units_percent <= configuration['writes_lower_threshold']:
        new_value = self._calculate_decrease_writes(
            updated_throughput['write_units'],
            configuration['decrease_writes_with'])
        updated_throughput['update_needed'] = True
        updated_throughput['write_units'] = new_value

    # Handle throughput updates
    if updated_throughput['update_needed']:
        logger.info(
            'Changing provisioning to {0:d} reads and {1:d} writes'.format(
                int(updated_throughput['read_units']),
                int(updated_throughput['write_units'])))
        self._update_throughput(
            updated_throughput['read_units'],
            updated_throughput['write_units'])
    else:
        logger.info('No need to change provisioning')