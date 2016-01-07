# -*- coding: utf-8 -*-
""" Configuration handler """
import config

CONFIGURATION = None


def get_configuration(configuration=None):
    global CONFIGURATION
    if CONFIGURATION is None:
        CONFIGURATION = config.get_configuration(configuration)
    return CONFIGURATION


def set_configuration(configuration=None):
    global CONFIGURATION
    CONFIGURATION = config.get_configuration(configuration)


def get_configured_tables():
    """ Returns a list of all configured tables

    :returns: list -- List of tables
    """
    try:
        return get_configuration()['tables'].keys()
    except KeyError:
        return []


def get_global_option(option):
    """ Returns the value of the option

    :returns: str or None
    """
    try:
        return get_configuration()['global'][option]
    except KeyError:
        return None


def get_gsi_option(table_key, gsi_key, option):
    """ Returns the value of the option

    :type table_key: str
    :param table_key: Table key name
    :type gsi_key: str
    :param gsi_key: GSI key name
    :returns: str or None
    """
    try:
        return get_configuration()['tables'][table_key]['gsis'][gsi_key][option]
    except KeyError:
        return None


def get_logging_option(option):
    """ Returns the value of the option

    :returns: str or None
    """
    try:
        return get_configuration()['logging'][option]
    except KeyError:
        return None


def get_table_option(table_name, option):
    """ Returns the value of the option

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: str or None
    """
    try:
        return get_configuration()['tables'][table_name][option]
    except KeyError:
        return None
