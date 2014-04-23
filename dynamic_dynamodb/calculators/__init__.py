# -*- coding: utf-8 -*-
""" General approach to calucations """
from dynamic_dynamodb.log_handler import LOGGER as logger


def get_min_reads(current_provisioning, min_provisioned_reads, log_tag):
    """ Get the minimum number of reads to current_provisioning

    :type current_provisioning: int
    :param current_provisioning: Current provisioned reads
    :type min_provisioned_reads: int
    :param min_provisioned_reads: Configured min provisioned reads
    :returns: int -- Minimum number of reads
    """
    # Fallback value to ensure that we always have at least 1 read
    reads = 1

    if min_provisioned_reads:
        reads = int(min_provisioned_reads)

        if reads > int(current_provisioning * 2):
            reads = int(current_provisioning * 2)
            logger.debug(
                '{0} - '
                'Cannot reach min_provisioned_reads as max scale up '
                'is 100% of current provisioning'.format(log_tag))

    logger.debug(
        '{0} - Setting min provisioned reads to {1}'.format(
            log_tag, min_provisioned_reads))

    return reads


def get_min_writes(current_provisioning, min_provisioned_writes, log_tag):
    """ Get the minimum number of writes to current_provisioning

    :type current_provisioning: int
    :param current_provisioning: Current provisioned writes
    :type min_provisioned_writes: int
    :param min_provisioned_writes: Configured min provisioned writes
    :returns: int -- Minimum number of writes
    """
    # Fallback value to ensure that we always have at least 1 read
    writes = 1

    if min_provisioned_writes:
        writes = int(min_provisioned_writes)

        if writes > int(current_provisioning * 2):
            writes = int(current_provisioning * 2)
            logger.debug(
                '{0} - '
                'Cannot reach min_provisioned_writes as max scale up '
                'is 100% of current provisioning'.format(log_tag))

    logger.debug(
        '{0} - Setting min provisioned writes to {1}'.format(
            log_tag, min_provisioned_writes))

    return writes
