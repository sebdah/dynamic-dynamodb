# -*- coding: utf-8 -*-
""" Core components """
from boto.exception import JSONResponseError, BotoServerError

from dynamic_dynamodb import calculators
from dynamic_dynamodb.aws import dynamodb, sns
from dynamic_dynamodb.core import circuit_breaker
from dynamic_dynamodb.statistics import table as table_stats
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_table_option, get_global_option


def ensure_provisioning(
        table_name, key_name,
        num_consec_read_checks,
        num_consec_write_checks):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    :type num_consec_read_checks: int
    :param num_consec_read_checks: How many consecutive checks have we had
    :type num_consec_write_checks: int
    :param num_consec_write_checks: How many consecutive checks have we had
    :returns: (int, int) -- num_consec_read_checks, num_consec_write_checks
    """

    if get_global_option('circuit_breaker_url'):
        if circuit_breaker.is_open():
            logger.warning('Circuit breaker is OPEN!')
            return (0, 0)

    # Handle throughput alarm checks
    __ensure_provisioning_alarm(table_name, key_name)

    try:
        read_update_needed, updated_read_units, num_consec_read_checks = \
            __ensure_provisioning_reads(
                table_name,
                key_name,
                num_consec_read_checks)
        write_update_needed, updated_write_units, num_consec_write_checks = \
            __ensure_provisioning_writes(
                table_name,
                key_name,
                num_consec_write_checks)

        if read_update_needed:
            num_consec_read_checks = 0

        if write_update_needed:
            num_consec_write_checks = 0

        # Handle throughput updates
        if read_update_needed or write_update_needed:
            logger.info(
                '{0} - Changing provisioning to {1:d} '
                'read units and {2:d} write units'.format(
                    table_name,
                    int(updated_read_units),
                    int(updated_write_units)))
            __update_throughput(
                table_name,
                key_name,
                updated_read_units,
                updated_write_units)
        else:
            logger.info('{0} - No need to change provisioning'.format(
                table_name))
    except JSONResponseError:
        raise
    except BotoServerError:
        raise

    return num_consec_read_checks, num_consec_write_checks


def __calculate_always_decrease_rw_values(
        table_name, read_units, provisioned_reads,
        write_units, provisioned_writes):
    """ Calculate values for always-decrease-rw-together

    This will only return reads and writes decreases if both reads and writes
    are lower than the current provisioning


    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type read_units: int
    :param read_units: New read unit provisioning
    :type provisioned_reads: int
    :param provisioned_reads: Currently provisioned reads
    :type write_units: int
    :param write_units: New write unit provisioning
    :type provisioned_writes: int
    :param provisioned_writes: Currently provisioned writes
    :returns: (int, int) -- (reads, writes)
    """
    if read_units < provisioned_reads and write_units < provisioned_writes:
        return (read_units, write_units)

    if read_units < provisioned_reads:
        logger.info(
            '{0} - Reads could be decreased, but we are waiting for '
            'writes to get lower than the threshold before '
            'scaling down'.format(table_name))

        read_units = provisioned_reads

    elif write_units < provisioned_writes:
        logger.info(
            '{0} - Writes could be decreased, but we are waiting for '
            'reads to get lower than the threshold before '
            'scaling down'.format(table_name))

        write_units = provisioned_writes

    return (read_units, write_units)


def __ensure_provisioning_reads(table_name, key_name, num_consec_read_checks):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    :type num_consec_read_checks: int
    :param num_consec_read_checks: How many consecutive checks have we had
    :returns: (bool, int, int)
        update_needed, updated_read_units, num_consec_read_checks
    """
    if not get_table_option(key_name, 'enable_reads_autoscaling'):
        logger.info(
            '{0} - Autoscaling of reads has been disabled'.format(table_name))
        return False, dynamodb.get_provisioned_table_read_units(table_name), 0

    update_needed = False
    try:
        current_read_units = dynamodb.get_provisioned_table_read_units(
            table_name)
        consumed_read_units_percent = \
            table_stats.get_consumed_read_units_percent(table_name)
        throttled_read_count = \
            table_stats.get_throttled_read_event_count(table_name)
        reads_upper_threshold = \
            get_table_option(key_name, 'reads_upper_threshold')
        reads_lower_threshold = \
            get_table_option(key_name, 'reads_lower_threshold')
        throttled_reads_upper_threshold = \
            get_table_option(key_name, 'throttled_reads_upper_threshold')
        increase_reads_with = \
            get_table_option(key_name, 'increase_reads_with')
        increase_reads_unit = \
            get_table_option(key_name, 'increase_reads_unit')
        decrease_reads_with = \
            get_table_option(key_name, 'decrease_reads_with')
        decrease_reads_unit = \
            get_table_option(key_name, 'decrease_reads_unit')
        max_provisioned_reads = \
            get_table_option(key_name, 'max_provisioned_reads')
        num_read_checks_before_scale_down = \
            get_table_option(key_name, 'num_read_checks_before_scale_down')
        num_read_checks_reset_percent = \
            get_table_option(key_name, 'num_read_checks_reset_percent')
        prevent_scaling_down_reads_if_throttled_minutes = \
            get_table_option(key_name, 'prevent_scaling_down_reads_if_throttled_minutes')
    except JSONResponseError:
        raise
    except BotoServerError:
        raise

    # Set the updated units to the current read unit value
    updated_read_units = current_read_units

    # Reset consecutive reads if num_read_checks_reset_percent is reached
    if num_read_checks_reset_percent:

        if consumed_read_units_percent >= num_read_checks_reset_percent:

            logger.info(
                '{0} - Resetting the number of consecutive '
                'read checks. Reason: Consumed percent {1} is '
                'greater than reset percent: {2}'.format(
                    table_name,
                    consumed_read_units_percent,
                    num_read_checks_reset_percent))

            num_consec_read_checks = 0

    if (consumed_read_units_percent == 0 and not
            get_table_option(
                key_name, 'allow_scaling_down_reads_on_0_percent')):
        logger.info(
            '{0} - Scaling down reads is not done when usage is at 0%'.format(
                table_name))

    elif (prevent_scaling_down_reads_if_throttled_minutes > 0 and
          table_stats.get_throttled_read_event_count(table_name, prevent_scaling_down_reads_if_throttled_minutes * 60) > 0):

        logger.info(
            '{0} - Not scaling down reads due to throttled requests in the past {1} minutes.'.format(
                table_name,
                prevent_scaling_down_reads_if_throttled_minutes))

    elif consumed_read_units_percent >= reads_upper_threshold:

        if increase_reads_unit == 'percent':
            calculated_provisioning = calculators.increase_reads_in_percent(
                current_read_units,
                increase_reads_with,
                get_table_option(key_name, 'max_provisioned_reads'),
                table_name)
        else:
            calculated_provisioning = calculators.increase_reads_in_units(
                current_read_units,
                increase_reads_with,
                get_table_option(key_name, 'max_provisioned_reads'),
                table_name)

        if current_read_units != calculated_provisioning:
            logger.info(
                '{0} - Resetting the number of consecutive '
                'read checks. Reason: scale up event detected'.format(
                    table_name))
            num_consec_read_checks = 0
            update_needed = True
            updated_read_units = calculated_provisioning

    elif throttled_read_count > throttled_reads_upper_threshold:

        if throttled_reads_upper_threshold > 0:
            if increase_reads_unit == 'percent':
                calculated_provisioning = calculators.increase_reads_in_percent(
                    updated_read_units,
                    increase_reads_with,
                    get_table_option(key_name, 'max_provisioned_reads'),
                    table_name)
            else:
                calculated_provisioning = calculators.increase_reads_in_units(
                    updated_read_units,
                    increase_reads_with,
                    get_table_option(key_name, 'max_provisioned_reads'),
                    table_name)

            if current_read_units != calculated_provisioning:
                logger.info(
                    '{0} - Resetting the number of consecutive '
                    'read checks. Reason: scale up event detected'.format(
                        table_name))
                num_consec_read_checks = 0
                update_needed = True
                updated_read_units = calculated_provisioning

    elif consumed_read_units_percent <= reads_lower_threshold:

        if decrease_reads_unit == 'percent':
            calculated_provisioning = calculators.decrease_reads_in_percent(
                updated_read_units,
                decrease_reads_with,
                get_table_option(key_name, 'min_provisioned_reads'),
                table_name)
        else:
            calculated_provisioning = calculators.decrease_reads_in_units(
                updated_read_units,
                decrease_reads_with,
                get_table_option(key_name, 'min_provisioned_reads'),
                table_name)

        if current_read_units != calculated_provisioning:
            num_consec_read_checks = num_consec_read_checks + 1

            if num_consec_read_checks >= num_read_checks_before_scale_down:
                update_needed = True
                updated_read_units = calculated_provisioning

    if max_provisioned_reads:
        if int(updated_read_units) > int(max_provisioned_reads):
            update_needed = True
            updated_read_units = int(max_provisioned_reads)
            logger.info(
                'Will not increase writes over max-provisioned-reads '
                'limit ({0} writes)'.format(updated_read_units))

    logger.info('{0} - Consecutive read checks {1}/{2}'.format(
        table_name,
        num_consec_read_checks,
        num_read_checks_before_scale_down))

    return update_needed, updated_read_units, num_consec_read_checks


def __ensure_provisioning_writes(
        table_name, key_name, num_consec_write_checks):
    """ Ensure that provisioning of writes is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    :type num_consec_write_checks: int
    :param num_consec_write_checks: How many consecutive checks have we had
    :returns: (bool, int, int)
        update_needed, updated_write_units, num_consec_write_checks
    """
    if not get_table_option(key_name, 'enable_writes_autoscaling'):
        logger.info(
            '{0} - Autoscaling of reads has been disabled'.format(table_name))
        return False, dynamodb.get_provisioned_table_write_units(table_name), 0

    update_needed = False
    try:
        current_write_units = dynamodb.get_provisioned_table_write_units(
            table_name)
        consumed_write_units_percent = \
            table_stats.get_consumed_write_units_percent(table_name)
        throttled_write_count = \
            table_stats.get_throttled_write_event_count(table_name)
        writes_upper_threshold = \
            get_table_option(key_name, 'writes_upper_threshold')
        writes_lower_threshold = \
            get_table_option(key_name, 'writes_lower_threshold')
        throttled_writes_upper_threshold = \
            get_table_option(key_name, 'throttled_writes_upper_threshold')
        increase_writes_unit = \
            get_table_option(key_name, 'increase_writes_unit')
        increase_writes_with = \
            get_table_option(key_name, 'increase_writes_with')
        decrease_writes_unit = \
            get_table_option(key_name, 'decrease_writes_unit')
        decrease_writes_with = \
            get_table_option(key_name, 'decrease_writes_with')
        max_provisioned_writes = \
            get_table_option(key_name, 'max_provisioned_writes')
        num_write_checks_before_scale_down = \
            get_table_option(key_name, 'num_write_checks_before_scale_down')
        num_write_checks_reset_percent = \
            get_table_option(key_name, 'num_write_checks_reset_percent')
        prevent_scaling_down_writes_if_throttled_minutes = \
            get_table_option(key_name, 'prevent_scaling_down_writes_if_throttled_minutes')
    except JSONResponseError:
        raise
    except BotoServerError:
        raise

    # Set the updated units to the current read unit value
    updated_write_units = current_write_units

    # Reset consecutive write count num_write_checks_reset_percent is reached
    if num_write_checks_reset_percent:

        if consumed_write_units_percent >= num_write_checks_reset_percent:

            logger.info(
                '{0} - Resetting the number of consecutive '
                'write checks. Reason: Consumed percent {1} is '
                'greater than reset percent: {2}'.format(
                    table_name,
                    consumed_write_units_percent,
                    num_write_checks_reset_percent))

            num_consec_write_checks = 0

    # Check if we should update write provisioning
    if (consumed_write_units_percent == 0 and not
            get_table_option(
                key_name, 'allow_scaling_down_writes_on_0_percent')):

        logger.info(
            '{0} - Scaling down writes is not done when usage is at 0%'.format(
                table_name))

    elif (prevent_scaling_down_writes_if_throttled_minutes > 0 and
          table_stats.get_throttled_write_event_count(table_name, prevent_scaling_down_writes_if_throttled_minutes * 60) > 0):

        logger.info(
            '{0} - Not scaling down writes due to throttled requests in the past {1} minutes.'.format(
                table_name,
                prevent_scaling_down_writes_if_throttled_minutes))

    elif consumed_write_units_percent >= writes_upper_threshold:

        if increase_writes_unit == 'percent':
            calculated_provisioning = calculators.increase_writes_in_percent(
                current_write_units,
                increase_writes_with,
                get_table_option(key_name, 'max_provisioned_writes'),
                table_name)
        else:
            calculated_provisioning = calculators.increase_writes_in_units(
                current_write_units,
                increase_writes_with,
                get_table_option(key_name, 'max_provisioned_writes'),
                table_name)

        if current_write_units != calculated_provisioning:
            logger.info(
                '{0} - Resetting the number of consecutive '
                'write checks. Reason: scale up event detected'.format(
                    table_name))
            num_consec_write_checks = 0
            update_needed = True
            updated_write_units = calculated_provisioning

    elif throttled_write_count > throttled_writes_upper_threshold:

        if throttled_writes_upper_threshold > 0:
            if increase_writes_unit == 'percent':
                calculated_provisioning = \
                    calculators.increase_writes_in_percent(
                        current_write_units,
                        increase_writes_with,
                        get_table_option(key_name, 'max_provisioned_writes'),
                        table_name)
            else:
                calculated_provisioning = calculators.increase_writes_in_units(
                    current_write_units,
                    increase_writes_with,
                    get_table_option(key_name, 'max_provisioned_writes'),
                    table_name)

            if current_write_units != calculated_provisioning:
                logger.info(
                    '{0} - Resetting the number of consecutive '
                    'write checks. Reason: scale up event detected'.format(
                        table_name))
                num_consec_write_checks = 0
                update_needed = True
                updated_write_units = calculated_provisioning

    elif consumed_write_units_percent <= writes_lower_threshold:

        if decrease_writes_unit == 'percent':
            calculated_provisioning = calculators.decrease_writes_in_percent(
                current_write_units,
                decrease_writes_with,
                get_table_option(key_name, 'min_provisioned_writes'),
                table_name)
        else:
            calculated_provisioning = calculators.decrease_writes_in_units(
                current_write_units,
                decrease_writes_with,
                get_table_option(key_name, 'min_provisioned_writes'),
                table_name)

        if current_write_units != calculated_provisioning:
            num_consec_write_checks = num_consec_write_checks + 1

            if num_consec_write_checks >= num_write_checks_before_scale_down:
                update_needed = True
                updated_write_units = calculated_provisioning

    if max_provisioned_writes:
        if int(updated_write_units) > int(max_provisioned_writes):
            update_needed = True
            updated_write_units = int(max_provisioned_writes)
            logger.info(
                'Will not increase writes over max-provisioned-writes '
                'limit ({0} writes)'.format(updated_write_units))

    logger.info('{0} - Consecutive write checks {1}/{2}'.format(
        table_name,
        num_consec_write_checks,
        num_write_checks_before_scale_down))

    return update_needed, updated_write_units, num_consec_write_checks


def __update_throughput(table_name, key_name, read_units, write_units):
    """ Update throughput on the DynamoDB table

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    :type read_units: int
    :param read_units: New read unit provisioning
    :type write_units: int
    :param write_units: New write unit provisioning
    """
    try:
        current_ru = dynamodb.get_provisioned_table_read_units(table_name)
        current_wu = dynamodb.get_provisioned_table_write_units(table_name)
    except JSONResponseError:
        raise

    # Check table status
    try:
        table_status = dynamodb.get_table_status(table_name)
    except JSONResponseError:
        raise
    logger.debug('{0} - Table status is {1}'.format(table_name, table_status))
    if table_status != 'ACTIVE':
        logger.warning(
            '{0} - Not performing throughput changes when table '
            'is {1}'.format(table_name, table_status))
        return

    # If this setting is True, we will only scale down when
    # BOTH reads AND writes are low
    if get_table_option(key_name, 'always_decrease_rw_together'):
        read_units, write_units = __calculate_always_decrease_rw_values(
            table_name,
            read_units,
            current_ru,
            write_units,
            current_wu)

        if read_units == current_ru and write_units == current_wu:
            logger.info('{0} - No changes to perform'.format(table_name))
            return

    dynamodb.update_table_provisioning(
        table_name,
        key_name,
        int(read_units),
        int(write_units))


def __ensure_provisioning_alarm(table_name, key_name):
    """ Ensure that provisioning alarm threshold is not exceeded

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    """
    consumed_read_units_percent = \
        table_stats.get_consumed_read_units_percent(table_name)
    consumed_write_units_percent = \
        table_stats.get_consumed_write_units_percent(table_name)

    reads_upper_alarm_threshold = \
        get_table_option(key_name, 'reads-upper-alarm-threshold')
    reads_lower_alarm_threshold = \
        get_table_option(key_name, 'reads-lower-alarm-threshold')
    writes_upper_alarm_threshold = \
        get_table_option(key_name, 'writes-upper-alarm-threshold')
    writes_lower_alarm_threshold = \
        get_table_option(key_name, 'writes-lower-alarm-threshold')

    # Check upper alarm thresholds
    upper_alert_triggered = False
    upper_alert_message = []
    if (reads_upper_alarm_threshold > 0 and
            consumed_read_units_percent >= reads_upper_alarm_threshold):
        upper_alert_triggered = True
        upper_alert_message.append(
            '{0} - Consumed Read Capacity {1:d}% '
            'was greater than or equal to the upper '
            'alarm threshold {2:d}%\n'.format(
                table_name,
                consumed_read_units_percent,
                reads_upper_alarm_threshold))

    if (writes_upper_alarm_threshold > 0 and
            consumed_write_units_percent >= writes_upper_alarm_threshold):
        upper_alert_triggered = True
        upper_alert_message.append(
            '{0} - Consumed Write Capacity {1:d}% '
            'was greater than or equal to the upper alarm '
            'threshold {2:d}%\n'.format(
                table_name,
                consumed_write_units_percent,
                writes_upper_alarm_threshold))

    # Check lower alarm thresholds
    lower_alert_triggered = False
    lower_alert_message = []
    if (reads_lower_alarm_threshold > 0 and
            consumed_read_units_percent < reads_lower_alarm_threshold):
        lower_alert_triggered = True
        lower_alert_message.append(
            '{0} - Consumed Read Capacity {1:d}% '
            'was below the lower alarm threshold {2:d}%\n'.format(
                table_name,
                consumed_read_units_percent,
                reads_lower_alarm_threshold))

    if (writes_lower_alarm_threshold > 0 and
            consumed_write_units_percent < writes_lower_alarm_threshold):
        lower_alert_triggered = True
        lower_alert_message.append(
            '{0} - Consumed Write Capacity {1:d}% '
            'was below the lower alarm threshold {2:d}%\n'.format(
                table_name,
                consumed_write_units_percent,
                writes_lower_alarm_threshold))

    # Send alert if needed
    if upper_alert_triggered:
        logger.info(
            '{0} - Will send high provisioning alert'.format(table_name))
        sns.publish_table_notification(
            key_name,
            ''.join(upper_alert_message),
            ['high-throughput-alarm'],
            subject='ALARM: High Throughput for Table {0}'.format(table_name))
    elif lower_alert_triggered:
        logger.info(
            '{0} - Will send low provisioning alert'.format(table_name))
        sns.publish_table_notification(
            key_name,
            ''.join(lower_alert_message),
            ['low-throughput-alarm'],
            subject='ALARM: Low Throughput for Table {0}'.format(table_name))
    else:
        logger.debug('{0} - Throughput alarm thresholds not crossed'.format(
            table_name))
