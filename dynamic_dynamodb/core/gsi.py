""" Core components """
from dynamic_dynamodb.core import dynamodb, circuit_breaker
from dynamic_dynamodb.log_handler import LOGGER as logger
from dynamic_dynamodb.config_handler import get_global_option


def ensure_gsi_provisioning(table_name, key_name):
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
        index_name = gsi[u'IndexName']
        current_ru = gsi[u'ProvisionedThroughput'][u'ReadCapacityUnits']
        current_wu = gsi[u'ProvisionedThroughput'][u'WriteCapacityUnits']
        logger.info(
            '{0} - GSI: {1} - '
            'Current provisioning is {2} read and {3} write units'.format(
                table_name,
                index_name,
                current_ru,
                current_wu))
