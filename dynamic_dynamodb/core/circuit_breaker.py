# -*- coding: utf-8 -*-
""" Circuit breaker functionality """
import re
import sys

import requests

from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_global_option, \
    get_table_option, get_gsi_option


def is_open(table_name=None, table_key=None, gsi_name=None, gsi_key=None):
    """ Checks whether the circuit breaker is open

    :param table_name: Name of the table being checked
    :param table_key: Configuration key for table
    :param gsi_name: Name of the GSI being checked
    :param gsi_key: Configuration key for the GSI
    :returns: bool -- True if the circuit is open
    """
    logger.debug('Checking circuit breaker status')

    # Parse the URL to make sure it is OK
    pattern = re.compile(
        r'^(?P<scheme>http(s)?://)'
        r'((?P<username>.+):(?P<password>.+)@){0,1}'
        r'(?P<url>.*)$'
    )

    url = timeout = None
    if gsi_name:
        url = get_gsi_option(table_key, gsi_key, 'circuit_breaker_url')
        timeout = get_gsi_option(table_key, gsi_key, 'circuit_breaker_timeout')
    elif table_name:
        url = get_table_option(table_key, 'circuit_breaker_url')
        timeout = get_table_option(table_key, 'circuit_breaker_timeout')

    if not url:
        url = get_global_option('circuit_breaker_url')
        timeout = get_global_option('circuit_breaker_timeout')

    match = pattern.match(url)
    if not match:
        logger.error('Malformatted URL: {0}'.format(url))
        sys.exit(1)

    use_basic_auth = False
    if match.group('username') and match.group('password'):
        use_basic_auth = True

    # Make the actual URL to call
    auth = ()
    if use_basic_auth:
        url = '{scheme}{url}'.format(
            scheme=match.group('scheme'),
            url=match.group('url'))
        auth = (match.group('username'), match.group('password'))

    headers = {}
    if table_name:
        headers["x-table-name"] = table_name
    if gsi_name:
        headers["x-gsi-name"] = gsi_name

    # Make the actual request
    try:
        response = requests.get(
            url,
            auth=auth,
            timeout=timeout / 1000.00,
            headers=headers)
        if int(response.status_code) > 200 and int(response.status_code) < 300:
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
