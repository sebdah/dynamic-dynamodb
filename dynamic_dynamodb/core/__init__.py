""" Core components """
import re
import sys
import datetime

from dynamic_dynamodb.core import dynamodb
from dynamic_dynamodb.core import statistics
from dynamic_dynamodb.core import calculators
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_table_option, get_global_option

import requests
from boto.exception import DynamoDBResponseError


def ensure_provisioning(table_name, key_name):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    """
    if get_global_option('circuit_breaker_url'):
        if __circuit_breaker_is_open():
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
        update_throughput(
            table_name, updated_read_units, updated_write_units, key_name)
    else:
        logger.info('{0} - No need to change provisioning'.format(table_name))


def __circuit_breaker_is_open():
    """ Checks wether the circuit breaker is open

    :returns: bool -- True if the circuit is open
    """
    logger.debug('Checking circuit breaker status')

    # Parse the URL to make sure it is OK
    pattern = re.compile(
        r'^(?P<scheme>http(s)?://)'
        r'((?P<username>.+):(?P<password>.+)@){0,1}'
        r'(?P<url>.*)$'
    )
    match = pattern.match(get_global_option('circuit_breaker_url'))

    if not match:
        logger.error('Malformatted URL: {0}'.format(
            get_global_option('circuit_breaker_url')))
        sys.exit(1)

    use_basic_auth = False
    if match.group('username') and match.group('password'):
        use_basic_auth = True

    # Make the actual URL to call
    if use_basic_auth:
        url = '{scheme}{url}'.format(
            scheme=match.group('scheme'),
            url=match.group('url'))
        auth = (match.group('username'), match.group('password'))
    else:
        url = get_global_option('circuit_breaker_url')
        auth = ()

    # Make the actual request
    try:
        response = requests.get(
            url,
            auth=auth,
            timeout=get_global_option('circuit_breaker_timeout') / 1000.00)
        if int(response.status_code) == 200:
            logger.info('Circuit breaker is closed')
            return False
        else:
            logger.warning(
                'Circuit breaker returned with status code {0:d}'.format(
                    response.status_code))

    except requests.exceptions.SSLError as error:
        logger.warning('Circuit breaker: {0}'.format(error))
    except requests.exceptions.Timeout as error:
        logger.warning('Circuit breaker: {0}'.format(error))
    except requests.exceptions.ConnectionError as error:
        logger.warning('Circuit breaker: {0}'.format(error))
    except requests.exceptions.HTTPError as error:
        logger.warning('Circuit breaker: {0}'.format(error))
    except requests.exceptions.TooManyRedirects as error:
        logger.warning('Circuit breaker: {0}'.format(error))
    except Exception as error:
        logger.error('Unhandled exception: {0}'.format(error))
        logger.error(
            'Please file a bug at '
            'https://github.com/sebdah/dynamic-dynamodb/issues')

    return True


def __ensure_provisioning_reads(table_name, key_name):
    """ Ensure that provisioning is correct

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :type key_name: str
    :param key_name: Configuration option key name
    :returns: (bool, int) -- update_needed, updated_read_units
    """
    update_needed = False
    updated_read_units = statistics.get_provisioned_read_units(table_name)

    consumed_read_units_percent = \
        statistics.get_consumed_read_units_percent(table_name)

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
    updated_write_units = statistics.get_provisioned_write_units(table_name)

    consumed_write_units_percent = \
        statistics.get_consumed_write_units_percent(table_name)

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
                key_name)
        else:
            updated_provisioning = calculators.increase_writes_in_units(
                updated_write_units,
                get_table_option(key_name, 'increase_writes_with'),
                key_name)

        if updated_write_units != updated_provisioning:
            update_needed = True
            updated_write_units = updated_provisioning

    elif (consumed_write_units_percent <=
            get_table_option(key_name, 'writes_lower_threshold')):

        if get_table_option(key_name, 'decrease_writes_unit') == 'percent':
            updated_provisioning = calculators.decrease_writes_in_percent(
                updated_write_units,
                get_table_option(key_name, 'decrease_writes_with'),
                key_name)
        else:
            updated_provisioning = calculators.decrease_writes_in_units(
                updated_write_units,
                get_table_option(key_name, 'decrease_writes_with'),
                key_name)

        if updated_write_units != updated_provisioning:
            update_needed = True
            updated_write_units = updated_provisioning

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


def update_throughput(table_name, read_units, write_units, key_name):
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
    if table.status != 'ACTIVE':
        logger.warning(
            '{0} - Not performing throughput changes when table '
            'is in {1} state'.format(table_name, table.status))

    # If this setting is True, we will only scale down when
    # BOTH reads AND writes are low
    if get_table_option(key_name, 'always_decrease_rw_together'):
        if ((read_units < table.read_units) or
                (table.read_units == get_table_option(
                    key_name, 'min_provisioned_reads'))):
            if ((write_units < table.write_units) or
                    (table.write_units == get_table_option(
                        key_name, 'min_provisioned_writes'))):
                logger.info(
                    '{0} - Both reads and writes will be decreased'.format(
                        table_name))

        elif read_units < table.read_units:
            logger.info(
                '{0} - Will not decrease reads nor writes, waiting for '
                'both to become low before decrease'.format(table_name))
            read_units = table.read_units
        elif write_units < table.write_units:
            logger.info(
                '{0} - Will not decrease reads nor writes, waiting for '
                'both to become low before decrease'.format(table_name))
            write_units = table.write_units

    if read_units == table.read_units and write_units == table.write_units:
        logger.debug('{0} - No need to update provisioning')
        return

    if not get_global_option('dry_run'):
        try:
            table.update_throughput(int(read_units), int(write_units))
            logger.info('Provisioning updated')
        except DynamoDBResponseError as error:
            dynamodb_error = error.body['__type'].rsplit('#', 1)[1]
            if dynamodb_error == 'LimitExceededException':
                logger.warning(
                    '{0} - {1}'.format(table_name, error.body['message']))

                if int(read_units) > table.read_units:
                    logger.info('{0} - Scaling up reads to {1:d}'.format(
                        table_name,
                        int(read_units)))
                    update_throughput(
                        table_name,
                        int(read_units),
                        int(table.write_units),
                        key_name)

                elif int(write_units) > table.write_units:
                    logger.info('{0} - Scaling up writes to {1:d}'.format(
                        table_name,
                        int(write_units)))
                    update_throughput(
                        table_name,
                        int(table.read_units),
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
