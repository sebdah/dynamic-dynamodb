# -*- coding: utf-8 -*-
""" Core components """
from boto.exception import JSONResponseError, BotoServerError

from dynamic_dynamodb import calculators
from dynamic_dynamodb.aws import dynamodb, sns
from dynamic_dynamodb.core import circuit_breaker
from dynamic_dynamodb.statistics import gsi as gsi_stats
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_global_option, get_gsi_option


def ensure_provisioning(
        table_name, table_key, gsi_name, gsi_key,
        num_consec_read_checks, num_consec_write_checks):
    """ Ensure that provisioning is correct for Global Secondary Indexes

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type gsi_key: str
    :param gsi_key: GSI configuration option key name
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

    logger.info(
        '{0} - Will ensure provisioning for global secondary index {1}'.format(
            table_name, gsi_name))

    # Handle throughput alarm checks
    __ensure_provisioning_alarm(table_name, table_key, gsi_name, gsi_key)

    try:
        read_update_needed, updated_read_units, num_consec_read_checks = \
            __ensure_provisioning_reads(
                table_name,
                table_key,
                gsi_name,
                gsi_key,
                num_consec_read_checks)
        write_update_needed, updated_write_units, num_consec_write_checks = \
            __ensure_provisioning_writes(
                table_name,
                table_key,
                gsi_name,
                gsi_key,
                num_consec_write_checks)

        if read_update_needed:
            num_consec_read_checks = 0

        if write_update_needed:
            num_consec_write_checks = 0

        # Handle throughput updates
        if read_update_needed or write_update_needed:
            logger.info(
                '{0} - GSI: {1} - Changing provisioning to {2:f} '
                'read units and {3:f} write units'.format(
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
    except JSONResponseError:
        raise
    except BotoServerError:
        raise

    return num_consec_read_checks, num_consec_write_checks


def __calculate_always_decrease_rw_values(
        table_name, gsi_name, read_units, provisioned_reads,
        write_units, provisioned_writes):
    """ Calculate values for always-decrease-rw-together

    This will only return reads and writes decreases if both reads and writes
    are lower than the current provisioning


    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type gsi_name: str
    :param gsi_name: Name of the GSI
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
    if read_units <= provisioned_reads and write_units <= provisioned_writes:
        return (read_units, write_units)

    if read_units < provisioned_reads:
        logger.info(
            '{0} - GSI: {1} - Reads could be decreased, '
            'but we are waiting for writes to get lower than the threshold '
            'before scaling down'.format(table_name, gsi_name))

        read_units = provisioned_reads

    elif write_units < provisioned_writes:
        logger.info(
            '{0} - GSI: {1} - Writes could be decreased, '
            'but we are waiting for reads to get lower than the threshold '
            'before scaling down'.format(table_name, gsi_name))

        write_units = provisioned_writes

    return (read_units, write_units)


def __ensure_provisioning_reads(
        table_name, table_key, gsi_name, gsi_key, num_consec_read_checks):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type gsi_key: str
    :param gsi_key: Configuration option key name
    :type num_consec_read_checks: int
    :param num_consec_read_checks: How many consecutive checks have we had
    :returns: (bool, int, int)
        update_needed, updated_read_units, num_consec_read_checks
    """
    if not get_gsi_option(table_key, gsi_key, 'enable_reads_autoscaling'):
        logger.info(
            '{0} - GSI: {1} - '
            'Autoscaling of reads has been disabled'.format(
                table_name, gsi_name))
        return False, dynamodb.get_provisioned_gsi_read_units(
            table_name, gsi_name), 0

    update_needed = False
    try:
        lookback_window_start = get_gsi_option(
            table_key, gsi_key, 'lookback_window_start')
        current_read_units = dynamodb.get_provisioned_gsi_read_units(
            table_name, gsi_name)
        consumed_read_units_percent = \
            gsi_stats.get_consumed_read_units_percent(
                table_name, gsi_name, lookback_window_start)
        throttled_read_count = \
            gsi_stats.get_throttled_read_event_count(
                table_name, gsi_name, lookback_window_start)
        throttled_by_provisioned_read_percent = \
            gsi_stats.get_throttled_by_provisioned_read_event_percent(
                table_name, gsi_name, lookback_window_start)
        throttled_by_consumed_read_percent = \
            gsi_stats.get_throttled_by_consumed_read_percent(
                table_name, gsi_name, lookback_window_start)
        reads_upper_threshold = \
            get_gsi_option(table_key, gsi_key, 'reads_upper_threshold')
        reads_lower_threshold = \
            get_gsi_option(table_key, gsi_key, 'reads_lower_threshold')
        increase_reads_unit = \
            get_gsi_option(table_key, gsi_key, 'increase_reads_unit')
        decrease_reads_unit = \
            get_gsi_option(table_key, gsi_key, 'decrease_reads_unit')
        increase_reads_with = \
            get_gsi_option(table_key, gsi_key, 'increase_reads_with')
        decrease_reads_with = \
            get_gsi_option(table_key, gsi_key, 'decrease_reads_with')
        throttled_reads_upper_threshold = \
            get_gsi_option(
                table_key, gsi_key, 'throttled_reads_upper_threshold')
        min_provisioned_reads = \
            get_gsi_option(table_key, gsi_key, 'min_provisioned_reads')
        max_provisioned_reads = \
            get_gsi_option(table_key, gsi_key, 'max_provisioned_reads')
        num_read_checks_before_scale_down = \
            get_gsi_option(
                table_key, gsi_key, 'num_read_checks_before_scale_down')
        num_read_checks_reset_percent = \
            get_gsi_option(table_key, gsi_key, 'num_read_checks_reset_percent')
        increase_throttled_by_provisioned_reads_unit = \
            get_gsi_option(
                table_key,
                gsi_key,
                'increase_throttled_by_provisioned_reads_unit')
        increase_throttled_by_provisioned_reads_scale = \
            get_gsi_option(
                table_key,
                gsi_key,
                'increase_throttled_by_provisioned_reads_scale')
        increase_throttled_by_consumed_reads_unit = \
            get_gsi_option(
                table_key,
                gsi_key,
                'increase_throttled_by_consumed_reads_unit')
        increase_throttled_by_consumed_reads_scale = \
            get_gsi_option(
                table_key,
                gsi_key,
                'increase_throttled_by_consumed_reads_scale')
        increase_consumed_reads_unit = \
            get_gsi_option(table_key, gsi_key, 'increase_consumed_reads_unit')
        increase_consumed_reads_with = \
            get_gsi_option(table_key, gsi_key, 'increase_consumed_reads_with')
        increase_consumed_reads_scale = \
            get_gsi_option(table_key, gsi_key, 'increase_consumed_reads_scale')
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
                '{0} - GSI: {1} - Resetting the number of consecutive '
                'read checks. Reason: Consumed percent {2} is '
                'greater than reset percent: {3}'.format(
                    table_name,
                    gsi_name,
                    consumed_read_units_percent,
                    num_read_checks_reset_percent))

            num_consec_read_checks = 0

    if (consumed_read_units_percent == 0 and not
            get_gsi_option(
                table_key,
                gsi_key,
                'allow_scaling_down_reads_on_0_percent')):

        logger.info(
            '{0} - GSI: {1} - '
            'Scaling down reads is not done when usage is at 0%'.format(
                table_name, gsi_name))

    # Exit if up scaling has been disabled
    if not get_gsi_option(table_key, gsi_key, 'enable_reads_up_scaling'):
        logger.debug(
            '{0} - GSI: {1} - Up scaling event detected. No action taken as '
            'scaling up reads has been disabled in the configuration'.format(
                table_name, gsi_name))

    else:

        # If local/granular values not specified use global values
        increase_consumed_reads_unit = \
            increase_consumed_reads_unit or increase_reads_unit
        increase_throttled_by_provisioned_reads_unit = \
            increase_throttled_by_provisioned_reads_unit or increase_reads_unit
        increase_throttled_by_consumed_reads_unit = \
            increase_throttled_by_consumed_reads_unit or increase_reads_unit

        increase_consumed_reads_with = \
            increase_consumed_reads_with or increase_reads_with

        # Initialise variables to store calculated provisioning
        throttled_by_provisioned_calculated_provisioning = scale_reader(
            increase_throttled_by_provisioned_reads_scale,
            throttled_by_provisioned_read_percent)
        throttled_by_consumed_calculated_provisioning = scale_reader(
            increase_throttled_by_consumed_reads_scale,
            throttled_by_consumed_read_percent)
        consumed_calculated_provisioning = scale_reader(
            increase_consumed_reads_scale,
            consumed_read_units_percent)
        throttled_count_calculated_provisioning = 0
        calculated_provisioning = 0

        # Increase needed due to high throttled to provisioned ratio
        if throttled_by_provisioned_calculated_provisioning:

            if increase_throttled_by_provisioned_reads_unit == 'percent':
                throttled_by_provisioned_calculated_provisioning = \
                    calculators.increase_reads_in_percent(
                        current_read_units,
                        throttled_by_provisioned_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                throttled_by_provisioned_calculated_provisioning = \
                    calculators.increase_reads_in_units(
                        current_read_units,
                        throttled_by_provisioned_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        # Increase needed due to high throttled to consumed ratio
        if throttled_by_consumed_calculated_provisioning:

            if increase_throttled_by_consumed_reads_unit == 'percent':
                throttled_by_consumed_calculated_provisioning = \
                    calculators.increase_reads_in_percent(
                        current_read_units,
                        throttled_by_consumed_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                throttled_by_consumed_calculated_provisioning = \
                    calculators.increase_reads_in_units(
                        current_read_units,
                        throttled_by_consumed_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        # Increase needed due to high CU consumption
        if consumed_calculated_provisioning:

            if increase_consumed_reads_unit == 'percent':
                consumed_calculated_provisioning = \
                    calculators.increase_reads_in_percent(
                        current_read_units,
                        consumed_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                consumed_calculated_provisioning = \
                    calculators.increase_reads_in_units(
                        current_read_units,
                        consumed_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        elif (reads_upper_threshold
                and consumed_read_units_percent > reads_upper_threshold
                and not increase_consumed_reads_scale):

            if increase_consumed_reads_unit == 'percent':
                consumed_calculated_provisioning = \
                    calculators.increase_reads_in_percent(
                        current_read_units,
                        increase_consumed_reads_with,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                consumed_calculated_provisioning = \
                    calculators.increase_reads_in_units(
                        current_read_units,
                        increase_consumed_reads_with,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        # Increase needed due to high throttling
        if (throttled_reads_upper_threshold
                and throttled_read_count > throttled_reads_upper_threshold):

            if increase_reads_unit == 'percent':
                throttled_count_calculated_provisioning = \
                    calculators.increase_reads_in_percent(
                        updated_read_units,
                        increase_reads_with,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                throttled_count_calculated_provisioning = \
                    calculators.increase_reads_in_units(
                        updated_read_units,
                        increase_reads_with,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_reads'),
                        consumed_read_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        # Determine which metric requires the most scaling
        if (throttled_by_provisioned_calculated_provisioning
                > calculated_provisioning):
            calculated_provisioning = \
                throttled_by_provisioned_calculated_provisioning
            scale_reason = (
                "due to throttled events by provisioned "
                "units threshold being exceeded")
        if (throttled_by_consumed_calculated_provisioning
                > calculated_provisioning):
            calculated_provisioning = \
                throttled_by_consumed_calculated_provisioning
            scale_reason = (
                "due to throttled events by consumed "
                "units threshold being exceeded")
        if consumed_calculated_provisioning > calculated_provisioning:
            calculated_provisioning = consumed_calculated_provisioning
            scale_reason = "due to consumed threshold being exceeded"
        if throttled_count_calculated_provisioning > calculated_provisioning:
            calculated_provisioning = throttled_count_calculated_provisioning
            scale_reason = "due to throttled events threshold being exceeded"

        if calculated_provisioning > current_read_units:
            logger.info(
                '{0} - GSI: {1} - Resetting the number of consecutive '
                'read checks. Reason: scale up {2}'.format(
                    table_name, gsi_name, scale_reason))
            num_consec_read_checks = 0
            update_needed = True
            updated_read_units = calculated_provisioning

    # Decrease needed due to low CU consumption
    if (consumed_read_units_percent <= reads_lower_threshold
            and not update_needed):

        # Exit if down scaling has been disabled
        if not get_gsi_option(table_key, gsi_key, 'enable_reads_down_scaling'):
            logger.debug(
                '{0} - GSI: {1} - Down scaling event detected. '
                'No action taken as scaling '
                'down reads has been disabled in the configuration'.format(
                    table_name, gsi_name))
        else:
            if decrease_reads_unit == 'percent':
                calculated_provisioning = calculators.decrease_reads_in_percent(
                    current_read_units,
                    decrease_reads_with,
                    get_gsi_option(table_key, gsi_key, 'min_provisioned_reads'),
                    '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                calculated_provisioning = calculators.decrease_reads_in_units(
                    current_read_units,
                    decrease_reads_with,
                    get_gsi_option(table_key, gsi_key, 'min_provisioned_reads'),
                    '{0} - GSI: {1}'.format(table_name, gsi_name))

            if current_read_units != calculated_provisioning:
                # We need to look at how many times the num_consec_read_checks
                # integer has incremented and Compare to config file value
                num_consec_read_checks = num_consec_read_checks + 1

                if num_consec_read_checks >= num_read_checks_before_scale_down:
                    update_needed = True
                    updated_read_units = calculated_provisioning

    # Never go over the configured max provisioning
    if max_provisioned_reads:
        if int(updated_read_units) > int(max_provisioned_reads):
            update_needed = True
            updated_read_units = int(max_provisioned_reads)
            logger.info(
                '{0} - GSI: {1} - Will not increase writes over '
                'gsi-max-provisioned-reads '
                'limit ({2} writes)'.format(
                    table_name,
                    gsi_name,
                    updated_read_units))

    # Ensure that we have met the min-provisioning
    if min_provisioned_reads:
        if int(min_provisioned_reads) > int(updated_read_units):
            update_needed = True
            updated_read_units = int(min_provisioned_reads)
            logger.info(
                '{0} - GSI: {1} - Increasing reads to'
                'meet gsi-min-provisioned-reads '
                'limit ({2} reads)'.format(
                    table_name,
                    gsi_name,
                    updated_read_units))

    logger.info('{0} - GSI: {1} - Consecutive read checks {2}/{3}'.format(
        table_name,
        gsi_name,
        num_consec_read_checks,
        num_read_checks_before_scale_down))

    return update_needed, updated_read_units, num_consec_read_checks


def __ensure_provisioning_writes(
        table_name, table_key, gsi_name, gsi_key, num_consec_write_checks):
    """ Ensure that provisioning of writes is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type gsi_key: str
    :param gsi_key: Configuration option key name
    :type num_consec_write_checks: int
    :param num_consec_write_checks: How many consecutive checks have we had
    :returns: (bool, int, int)
        update_needed, updated_write_units, num_consec_write_checks
    """
    if not get_gsi_option(table_key, gsi_key, 'enable_writes_autoscaling'):
        logger.info(
            '{0} - GSI: {1} - '
            'Autoscaling of writes has been disabled'.format(
                table_name, gsi_name))
        return False, dynamodb.get_provisioned_gsi_write_units(
            table_name, gsi_name), 0

    update_needed = False
    try:
        lookback_window_start = get_gsi_option(
            table_key, gsi_key, 'lookback_window_start')
        current_write_units = dynamodb.get_provisioned_gsi_write_units(
            table_name, gsi_name)
        consumed_write_units_percent = \
            gsi_stats.get_consumed_write_units_percent(
                table_name, gsi_name, lookback_window_start)
        throttled_write_count = \
            gsi_stats.get_throttled_write_event_count(
                table_name, gsi_name, lookback_window_start)
        throttled_by_provisioned_write_percent = \
            gsi_stats.get_throttled_by_provisioned_write_event_percent(
                table_name, gsi_name, lookback_window_start)
        throttled_by_consumed_write_percent = \
            gsi_stats.get_throttled_by_consumed_write_percent(
                table_name, gsi_name, lookback_window_start)
        writes_upper_threshold = \
            get_gsi_option(table_key, gsi_key, 'writes_upper_threshold')
        writes_lower_threshold = \
            get_gsi_option(table_key, gsi_key, 'writes_lower_threshold')
        throttled_writes_upper_threshold = \
            get_gsi_option(
                table_key, gsi_key, 'throttled_writes_upper_threshold')
        increase_writes_unit = \
            get_gsi_option(table_key, gsi_key, 'increase_writes_unit')
        increase_writes_with = \
            get_gsi_option(table_key, gsi_key, 'increase_writes_with')
        decrease_writes_unit = \
            get_gsi_option(table_key, gsi_key, 'decrease_writes_unit')
        decrease_writes_with = \
            get_gsi_option(table_key, gsi_key, 'decrease_writes_with')
        min_provisioned_writes = \
            get_gsi_option(table_key, gsi_key, 'min_provisioned_writes')
        max_provisioned_writes = \
            get_gsi_option(table_key, gsi_key, 'max_provisioned_writes')
        num_write_checks_before_scale_down = \
            get_gsi_option(
                table_key, gsi_key, 'num_write_checks_before_scale_down')
        num_write_checks_reset_percent = \
            get_gsi_option(table_key, gsi_key, 'num_write_checks_reset_percent')
        increase_throttled_by_provisioned_writes_unit = \
            get_gsi_option(
                table_key,
                gsi_key,
                'increase_throttled_by_provisioned_writes_unit')
        increase_throttled_by_provisioned_writes_scale = \
            get_gsi_option(
                table_key,
                gsi_key,
                'increase_throttled_by_provisioned_writes_scale')
        increase_throttled_by_consumed_writes_unit = \
            get_gsi_option(
                table_key,
                gsi_key,
                'increase_throttled_by_consumed_writes_unit')
        increase_throttled_by_consumed_writes_scale = \
            get_gsi_option(
                table_key,
                gsi_key,
                'increase_throttled_by_consumed_writes_scale')
        increase_consumed_writes_unit = \
            get_gsi_option(table_key, gsi_key, 'increase_consumed_writes_unit')
        increase_consumed_writes_with = \
            get_gsi_option(table_key, gsi_key, 'increase_consumed_writes_with')
        increase_consumed_writes_scale = \
            get_gsi_option(table_key, gsi_key, 'increase_consumed_writes_scale')
    except JSONResponseError:
        raise
    except BotoServerError:
        raise

    # Set the updated units to the current write unit value
    updated_write_units = current_write_units

    # Reset write consecutive count if num_write_checks_reset_percent is reached
    if num_write_checks_reset_percent:

        if consumed_write_units_percent >= num_write_checks_reset_percent:

            logger.info(
                '{0} - GSI: {1} - Resetting the number of consecutive '
                'write checks. Reason: Consumed percent {2} is '
                'greater than reset percent: {3}'.format(
                    table_name,
                    gsi_name,
                    consumed_write_units_percent,
                    num_write_checks_reset_percent))

            num_consec_write_checks = 0

    # Check if we should update write provisioning
    if (consumed_write_units_percent == 0 and not get_gsi_option(
            table_key, gsi_key, 'allow_scaling_down_writes_on_0_percent')):

        logger.info(
            '{0} - GSI: {1} - '
            'Scaling down writes is not done when usage is at 0%'.format(
                table_name, gsi_name))

    # Exit if up scaling has been disabled
    if not get_gsi_option(table_key, gsi_key, 'enable_writes_up_scaling'):
        logger.debug(
            '{0} - GSI: {1} - Up scaling event detected. No action taken as '
            'scaling up writes has been disabled in the configuration'.format(
                table_name, gsi_name))

    else:

        # If local/granular values not specified use global values
        increase_consumed_writes_unit = \
            increase_consumed_writes_unit or increase_writes_unit
        increase_throttled_by_provisioned_writes_unit = (
            increase_throttled_by_provisioned_writes_unit
            or increase_writes_unit)
        increase_throttled_by_consumed_writes_unit = \
            increase_throttled_by_consumed_writes_unit or increase_writes_unit

        increase_consumed_writes_with = \
            increase_consumed_writes_with or increase_writes_with

        # Initialise variables to store calculated provisioning
        throttled_by_provisioned_calculated_provisioning = scale_reader(
            increase_throttled_by_provisioned_writes_scale,
            throttled_by_provisioned_write_percent)
        throttled_by_consumed_calculated_provisioning = scale_reader(
            increase_throttled_by_consumed_writes_scale,
            throttled_by_consumed_write_percent)
        consumed_calculated_provisioning = scale_reader(
            increase_consumed_writes_scale,
            consumed_write_units_percent)
        throttled_count_calculated_provisioning = 0
        calculated_provisioning = 0

        # Increase needed due to high throttled to provisioned ratio
        if throttled_by_provisioned_calculated_provisioning:

            if increase_throttled_by_provisioned_writes_unit == 'percent':
                throttled_by_provisioned_calculated_provisioning = \
                    calculators.increase_writes_in_percent(
                        current_write_units,
                        throttled_by_provisioned_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                throttled_by_provisioned_calculated_provisioning = \
                    calculators.increase_writes_in_units(
                        current_write_units,
                        throttled_by_provisioned_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        # Increase needed due to high throttled to consumed ratio
        if throttled_by_consumed_calculated_provisioning:

            if increase_throttled_by_consumed_writes_unit == 'percent':
                throttled_by_consumed_calculated_provisioning = \
                    calculators.increase_writes_in_percent(
                        current_write_units,
                        throttled_by_consumed_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                throttled_by_consumed_calculated_provisioning = \
                    calculators.increase_writes_in_units(
                        current_write_units,
                        throttled_by_consumed_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        # Increase needed due to high CU consumption
        if consumed_calculated_provisioning:

            if increase_consumed_writes_unit == 'percent':
                consumed_calculated_provisioning = \
                    calculators.increase_writes_in_percent(
                        current_write_units,
                        consumed_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                consumed_calculated_provisioning = \
                    calculators.increase_writes_in_units(
                        current_write_units,
                        consumed_calculated_provisioning,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        elif (writes_upper_threshold
                and consumed_write_units_percent > writes_upper_threshold
                and not increase_consumed_writes_scale):

            if increase_consumed_writes_unit == 'percent':
                consumed_calculated_provisioning = \
                    calculators.increase_writes_in_percent(
                        current_write_units,
                        increase_consumed_writes_with,
                        get_gsi_option(
                            table_key,
                            gsi_key,
                            'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                consumed_calculated_provisioning = \
                    calculators.increase_writes_in_units(
                        current_write_units,
                        increase_consumed_writes_with,
                        get_gsi_option(
                            table_key, gsi_key, 'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        # Increase needed due to high throttling
        if (throttled_writes_upper_threshold
                and throttled_write_count > throttled_writes_upper_threshold):

            if increase_writes_unit == 'percent':
                throttled_count_calculated_provisioning = \
                    calculators.increase_writes_in_percent(
                        updated_write_units,
                        increase_writes_with,
                        get_gsi_option(
                            table_key, gsi_key, 'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                throttled_count_calculated_provisioning = \
                    calculators.increase_writes_in_units(
                        updated_write_units,
                        increase_writes_with,
                        get_gsi_option(
                            table_key, gsi_key, 'max_provisioned_writes'),
                        consumed_write_units_percent,
                        '{0} - GSI: {1}'.format(table_name, gsi_name))

        # Determine which metric requires the most scaling
        if (throttled_by_provisioned_calculated_provisioning
                > calculated_provisioning):
            calculated_provisioning = \
                throttled_by_provisioned_calculated_provisioning
            scale_reason = (
                "due to throttled events by provisioned "
                "units threshold being exceeded")
        if (throttled_by_consumed_calculated_provisioning
                > calculated_provisioning):
            calculated_provisioning = \
                throttled_by_consumed_calculated_provisioning
            scale_reason = (
                "due to throttled events by consumed "
                "units threshold being exceeded")
        if consumed_calculated_provisioning > calculated_provisioning:
            calculated_provisioning = consumed_calculated_provisioning
            scale_reason = "due to consumed threshold being exceeded"
        if throttled_count_calculated_provisioning > calculated_provisioning:
            calculated_provisioning = throttled_count_calculated_provisioning
            scale_reason = "due to throttled events threshold being exceeded"

        if calculated_provisioning > current_write_units:
            logger.info(
                '{0} - GSI: {1} - Resetting the number of consecutive '
                'write checks. Reason: scale up {2}'.format(
                    table_name, gsi_name, scale_reason))
            num_consec_write_checks = 0
            update_needed = True
            updated_write_units = calculated_provisioning

    # Decrease needed due to low CU consumption
    if (consumed_write_units_percent
            <= writes_lower_threshold and not update_needed):

        # Exit if down scaling has been disabled
        if not get_gsi_option(table_key, gsi_key, 'enable_writes_down_scaling'):
            logger.debug(
                '{0} - GSI: {1} - Down scaling event detected. '
                'No action taken as scaling '
                'down writes has been disabled in the configuration'.format(
                    table_name, gsi_name))
        else:
            if decrease_writes_unit == 'percent':
                calculated_provisioning = \
                    calculators.decrease_writes_in_percent(
                        current_write_units,
                        decrease_writes_with,
                        get_gsi_option(
                            table_key, gsi_key, 'min_provisioned_writes'),
                        '{0} - GSI: {1}'.format(table_name, gsi_name))
            else:
                calculated_provisioning = calculators.decrease_writes_in_units(
                    current_write_units,
                    decrease_writes_with,
                    get_gsi_option(
                        table_key, gsi_key, 'min_provisioned_writes'),
                    '{0} - GSI: {1}'.format(table_name, gsi_name))

            if current_write_units != calculated_provisioning:
                num_consec_write_checks = num_consec_write_checks + 1

                if (num_consec_write_checks >=
                        num_write_checks_before_scale_down):
                    update_needed = True
                    updated_write_units = calculated_provisioning

    # Never go over the configured max provisioning
    if max_provisioned_writes:
        if int(updated_write_units) > int(max_provisioned_writes):
            update_needed = True
            updated_write_units = int(max_provisioned_writes)
            logger.info(
                '{0} - GSI: {1} - '
                'Will not increase writes over gsi-max-provisioned-writes '
                'limit ({2} writes)'.format(
                    table_name,
                    gsi_name,
                    updated_write_units))

    # Ensure that we have met the min-provisioning
    if min_provisioned_writes:
        if int(min_provisioned_writes) > int(updated_write_units):
            update_needed = True
            updated_write_units = int(min_provisioned_writes)
            logger.info(
                '{0} - GSI: {1} - Increasing writes to'
                'meet gsi-min-provisioned-writes '
                'limit ({2} writes)'.format(
                    table_name,
                    gsi_name,
                    updated_write_units))

    logger.info('{0} - GSI: {1} - Consecutive write checks {2}/{3}'.format(
        table_name,
        gsi_name,
        num_consec_write_checks,
        num_write_checks_before_scale_down))

    return update_needed, updated_write_units, num_consec_write_checks


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
    try:
        current_ru = dynamodb.get_provisioned_gsi_read_units(
            table_name, gsi_name)
        current_wu = dynamodb.get_provisioned_gsi_write_units(
            table_name, gsi_name)
    except JSONResponseError:
        raise

    # Check table status
    try:
        gsi_status = dynamodb.get_gsi_status(table_name, gsi_name)
    except JSONResponseError:
        raise

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
        read_units, write_units = __calculate_always_decrease_rw_values(
            table_name,
            gsi_name,
            read_units,
            current_ru,
            write_units,
            current_wu)

        if read_units == current_ru and write_units == current_wu:
            logger.info('{0} - GSI: {1} - No changes to perform'.format(
                table_name, gsi_name))
            return

    dynamodb.update_gsi_provisioning(
        table_name,
        table_key,
        gsi_name,
        gsi_key,
        int(read_units),
        int(write_units))


def __ensure_provisioning_alarm(table_name, table_key, gsi_name, gsi_key):
    """ Ensure that provisioning alarm threshold is not exceeded

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type table_key: str
    :param table_key: Table configuration option key name
    :type gsi_name: str
    :param gsi_name: Name of the GSI
    :type gsi_key: str
    :param gsi_key: Configuration option key name
    """
    lookback_window_start = get_gsi_option(
        table_key, gsi_key, 'lookback_window_start')
    consumed_read_units_percent = gsi_stats.get_consumed_read_units_percent(
        table_name, gsi_name, lookback_window_start)
    consumed_write_units_percent = gsi_stats.get_consumed_write_units_percent(
        table_name, gsi_name, lookback_window_start)

    reads_upper_alarm_threshold = \
        get_gsi_option(table_key, gsi_key, 'reads-upper-alarm-threshold')
    reads_lower_alarm_threshold = \
        get_gsi_option(table_key, gsi_key, 'reads-lower-alarm-threshold')
    writes_upper_alarm_threshold = \
        get_gsi_option(table_key, gsi_key, 'writes-upper-alarm-threshold')
    writes_lower_alarm_threshold = \
        get_gsi_option(table_key, gsi_key, 'writes-lower-alarm-threshold')

    # Check upper alarm thresholds
    upper_alert_triggered = False
    upper_alert_message = []
    if (reads_upper_alarm_threshold > 0 and
            consumed_read_units_percent >= reads_upper_alarm_threshold):
        upper_alert_triggered = True
        upper_alert_message.append(
            '{0} - GSI: {1} - Consumed Read Capacity {2:f}% '
            'was greater than or equal to the upper alarm '
            'threshold {3:f}%\n'.format(
                table_name,
                gsi_name,
                consumed_read_units_percent,
                reads_upper_alarm_threshold))

    if (writes_upper_alarm_threshold > 0 and
            consumed_write_units_percent >= writes_upper_alarm_threshold):
        upper_alert_triggered = True
        upper_alert_message.append(
            '{0} - GSI: {1} - Consumed Write Capacity {2:f}% '
            'was greater than or equal to the upper alarm '
            'threshold {3:f}%\n'.format(
                table_name,
                gsi_name,
                consumed_write_units_percent,
                writes_upper_alarm_threshold))

    # Check lower alarm thresholds
    lower_alert_triggered = False
    lower_alert_message = []
    if (reads_lower_alarm_threshold > 0 and
            consumed_read_units_percent < reads_lower_alarm_threshold):
        lower_alert_triggered = True
        lower_alert_message.append(
            '{0} - GSI: {1} - Consumed Read Capacity {2:f}% '
            'was below the lower alarm threshold {3:f}%\n'.format(
                table_name,
                gsi_name,
                consumed_read_units_percent,
                reads_lower_alarm_threshold))

    if (writes_lower_alarm_threshold > 0 and
            consumed_write_units_percent < writes_lower_alarm_threshold):
        lower_alert_triggered = True
        lower_alert_message.append(
            '{0} - GSI: {1} - Consumed Write Capacity {2:f}% '
            'was below the lower alarm threshold {3:f}%\n'.format(
                table_name,
                gsi_name,
                consumed_write_units_percent,
                writes_lower_alarm_threshold))

    # Send alert if needed
    if upper_alert_triggered:
        logger.info(
            '{0} - GSI: {1} - Will send high provisioning alert'.format(
                table_name, gsi_name))
        sns.publish_gsi_notification(
            table_key,
            gsi_key,
            ''.join(upper_alert_message),
            ['high-throughput-alarm'],
            subject='ALARM: High Throughput for Table {0} - GSI: {1}'.format(
                table_name, gsi_name))
    elif lower_alert_triggered:
        logger.info(
            '{0} - GSI: {1} - Will send low provisioning alert'.format(
                table_name, gsi_name))
        sns.publish_gsi_notification(
            table_key,
            gsi_key,
            ''.join(lower_alert_message),
            ['low-throughput-alarm'],
            subject='ALARM: Low Throughput for Table {0} - GSI: {1}'.format(
                table_name, gsi_name))
    else:
        logger.debug(
            '{0} - GSI: {1} - Throughput alarm thresholds not crossed'.format(
                table_name, gsi_name))


def scale_reader(provision_increase_scale, current_value):
    """

    :type provision_increase_scale: dict
    :param provision_increase_scale: dictionary with key being the scaling
        threshold and value being scaling amount
    :type current_value: float
    :param current_value: the current consumed units or throttled events
    :returns: (int) The amount to scale provisioning by
    """

    scale_value = 0
    if provision_increase_scale:
        for limits in sorted(provision_increase_scale.keys()):
            if current_value < limits:
                return scale_value
            else:
                scale_value = provision_increase_scale.get(limits)
        return scale_value
    else:
        return scale_value
