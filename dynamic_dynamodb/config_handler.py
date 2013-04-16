""" Configuration handler """
import config

CONFIGURATION = config.get_configuration()


def get_table_option(table_name, option):
    """ Returns the value of the option

    :type table_name: str
    :param table_name: Name of the DynamoDB table
    :returns: str
    """
    return CONFIGURATION['tables'][table_name][option]
