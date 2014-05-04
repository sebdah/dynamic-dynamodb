# -*- coding: utf-8 -*-
""" Circuit breaker functionality """
import re
import sys

import requests

from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_global_option


def is_open():
    """ Checks whether the circuit breaker is open

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
