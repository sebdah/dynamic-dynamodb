""" Configuration handler """
import config

CONFIGURATION = config.get_configuration()


def get_global_option(option):
    """ Returns the value of the option

    :returns: str
    """
    return CONFIGURATION['global'][option]


def get_logging_option(option):
    """ Returns the value of the option

    :returns: str
    """
    return CONFIGURATION['logging'][option]


def get_table_option(table_name, option):
    """ Returns the value of the option

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: str
    """
    return CONFIGURATION['tables'][table_name][option]
