# -*- coding: utf-8 -*-
""" Configuration management """
import sys
from dynamic_dynamodb.config import config_file_parser
from dynamic_dynamodb.config import command_line_parser

DEFAULT_OPTIONS = {
    'global': {
        # Command line only
        'config': None,
        'daemon': False,
        'instance': 'default',
        'dry_run': False,

        # [global]
        'region': 'us-east-1',
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
        'check_interval': 300,
        'circuit_breaker_url': None,
        'circuit_breaker_timeout': 10000.00
    },
    'logging': {
        # [logging]
        'log_file': None,
        'log_level': 'info',
        'log_config_file': None
    },
    'table': {
        'reads_lower_threshold': 30,
        'reads_upper_threshold': 90,
        'increase_reads_with': 50,
        'decrease_reads_with': 50,
        'increase_reads_unit': 'percent',
        'decrease_reads_unit': 'percent',
        'writes_lower_threshold': 30,
        'writes_upper_threshold': 90,
        'increase_writes_with': 50,
        'decrease_writes_with': 50,
        'increase_writes_unit': 'percent',
        'decrease_writes_unit': 'percent',
        'min_provisioned_reads': None,
        'max_provisioned_reads': None,
        'min_provisioned_writes': None,
        'max_provisioned_writes': None,
        'allow_scaling_down_reads_on_0_percent': False,
        'allow_scaling_down_writes_on_0_percent': False,
        'always_decrease_rw_together': False,
        'maintenance_windows': None,
    },
    'gsi': {
        'reads_lower_threshold': 30,
        'reads_upper_threshold': 90,
        'increase_reads_with': 50,
        'decrease_reads_with': 50,
        'increase_reads_unit': 'percent',
        'decrease_reads_unit': 'percent',
        'writes_lower_threshold': 30,
        'writes_upper_threshold': 90,
        'increase_writes_with': 50,
        'decrease_writes_with': 50,
        'increase_writes_unit': 'percent',
        'decrease_writes_unit': 'percent',
        'min_provisioned_reads': None,
        'max_provisioned_reads': None,
        'min_provisioned_writes': None,
        'max_provisioned_writes': None,
        'allow_scaling_down_reads_on_0_percent': False,
        'allow_scaling_down_writes_on_0_percent': False,
        'always_decrease_rw_together': False,
        'maintenance_windows': None,
    }
}


def get_configuration():
    """ Get the configuration from command line and config files """
    # This is the dict we will return
    configuration = {
        'global': {},
        'logging': {},
        'tables': {}
    }

    # Read the command line options
    cmd_line_options = command_line_parser.parse()

    # If a configuration file is specified, read that as well
    if 'config' in cmd_line_options:
        conf_file_options = config_file_parser.parse(
            cmd_line_options['config'])
    else:
        conf_file_options = None

    # Extract global config
    configuration['global'] = __get_global_options(
        cmd_line_options,
        conf_file_options)

    # Extract logging config
    configuration['logging'] = __get_logging_options(
        cmd_line_options,
        conf_file_options)

    # Extract table configuration
    # If the --table cmd line option is set, it indicates that only table
    # options from the command line should be used
    if 'table_name' in cmd_line_options:
        configuration['tables'] = __get_cmd_table_options(cmd_line_options)
    else:
        configuration['tables'] = __get_config_table_options(conf_file_options)

    # Ensure some basic rules
    __check_gsi_rules(configuration)
    __check_logging_rules(configuration)
    __check_table_rules(configuration)

    return configuration


def __get_cmd_table_options(cmd_line_options):
    """ Get all table options from the command line

    :type cmd_line_options: dict
    :param cmd_line_options: Dictionary with all command line options
    :returns: dict -- E.g. {'table_name': {}}
    """
    table_name = cmd_line_options['table_name']
    options = {table_name: {}}

    for option in DEFAULT_OPTIONS['table'].keys():
        options[table_name][option] = DEFAULT_OPTIONS['table'][option]

        if option in cmd_line_options:
            options[table_name][option] = cmd_line_options[option]

    return options


def __get_config_table_options(conf_file_options):
    """ Get all table options from the config file

    :type conf_file_options: dict
    :param conf_file_options: Dictionary with all config file options
    :returns: dict -- E.g. {'table_name': {}}
    """
    options = {}

    if not conf_file_options:
        return options

    for table_name in conf_file_options['tables']:
        options[table_name] = {}

        # Regular table options
        for option in DEFAULT_OPTIONS['table'].keys():
            options[table_name][option] = DEFAULT_OPTIONS['table'][option]

            if option in conf_file_options['tables'][table_name]:
                options[table_name][option] = \
                    conf_file_options['tables'][table_name][option]

        # GSI specific options
        if 'gsis' in conf_file_options['tables'][table_name]:
            for gsi_name in conf_file_options['tables'][table_name]['gsis']:
                for option in DEFAULT_OPTIONS['gsi'].keys():
                    if (option in conf_file_options[
                            'tables'][table_name]['gsis'][gsi_name]):
                        opt = conf_file_options[
                            'tables'][table_name]['gsis'][gsi_name][option]
                    else:
                        opt = DEFAULT_OPTIONS['gsi'][option]

                    if 'gsis' not in options[table_name]:
                        options[table_name]['gsis'] = {}

                    if gsi_name not in options[table_name]['gsis']:
                        options[table_name]['gsis'][gsi_name] = {}

                    options[table_name]['gsis'][gsi_name][option] = opt

    return options


def __get_global_options(cmd_line_options, conf_file_options=None):
    """ Get all global options

    :type cmd_line_options: dict
    :param cmd_line_options: Dictionary with all command line options
    :type conf_file_options: dict
    :param conf_file_options: Dictionary with all config file options
    :returns: dict
    """
    options = {}

    for option in DEFAULT_OPTIONS['global'].keys():
        options[option] = DEFAULT_OPTIONS['global'][option]

        if conf_file_options and option in conf_file_options:
            options[option] = conf_file_options[option]

        if cmd_line_options and option in cmd_line_options:
            options[option] = cmd_line_options[option]

    return options


def __get_logging_options(cmd_line_options, conf_file_options=None):
    """ Get all logging options

    :type cmd_line_options: dict
    :param cmd_line_options: Dictionary with all command line options
    :type conf_file_options: dict
    :param conf_file_options: Dictionary with all config file options
    :returns: dict
    """
    options = {}

    for option in DEFAULT_OPTIONS['logging'].keys():
        options[option] = DEFAULT_OPTIONS['logging'][option]

        if conf_file_options and option in conf_file_options:
            options[option] = conf_file_options[option]

        if cmd_line_options and option in cmd_line_options:
            options[option] = cmd_line_options[option]

    return options


def __check_gsi_rules(configuration):
    """ Do some basic checks on the configuraion """
    for table_name in configuration['tables']:
        if not 'gsis' in configuration['tables'][table_name]:
            continue

        for gsi_name in configuration['tables'][table_name]['gsis']:
            gsi = configuration['tables'][table_name]['gsis'][gsi_name]
            # Check that increase/decrease units is OK
            valid_units = ['percent', 'units']
            if gsi['increase_reads_unit'] not in valid_units:
                print(
                    'increase-reads-with must be set to '
                    'either percent or units')
                sys.exit(1)
            if gsi['decrease_reads_unit'] not in valid_units:
                print(
                    'decrease-reads-with must be set to '
                    'either percent or units')
                sys.exit(1)
            if gsi['increase_writes_unit'] not in valid_units:
                print(
                    'increase-writes-with must be set to '
                    'either percent or units')
                sys.exit(1)
            if gsi['decrease_writes_unit'] not in valid_units:
                print(
                    'decrease-writes-with must be set to '
                    'either percent or units')
                sys.exit(1)

            # Check that increase_writes_with is not > 100
            if (gsi['increase_writes_unit'] == 'percent' and
                    gsi['increase_writes_with'] > 100):

                print(
                    'You can not increase the GSI throughput with more '
                    'than 100% at a time. '
                    'Setting --increase-writes-with to 100.')
                gsi['increase_writes_with'] = 100

            # Check that increase_reads_with is not > 100
            if (gsi['increase_reads_unit'] == 'percent' and
                    gsi['increase_reads_with'] > 100):
                print(
                    'You can not increase the GSI throughput with more '
                    'than 100% at a time. '
                    'Setting --increase-reads-with to 100.')
                gsi['increase_reads_with'] = 100

            # Ensure values > 1 for some important configuration options
            options = [
                'reads_lower_threshold',
                'reads_upper_threshold',
                'increase_reads_with',
                'decrease_reads_with',
                'writes_lower_threshold',
                'writes_upper_threshold',
                'increase_writes_with',
                'decrease_writes_with',
                'min_provisioned_reads',
                'max_provisioned_reads',
                'min_provisioned_writes',
                'max_provisioned_writes'
            ]
            for option in options:
                if gsi[option] < 1:
                    print('{0} may not be lower than 1 for GSI {1}'.format(
                        option, gsi_name))
                    sys.exit(1)

            if (int(gsi['min_provisioned_reads']) >
                    int(gsi['max_provisioned_reads'])):
                print(
                    'min_provisioned_reads ({0}) may not be higher than '
                    'max_provisioned_reads ({1}) for GSI {2}'.format(
                        gsi['min_provisioned_reads'],
                        gsi['max_provisioned_reads'],
                        gsi_name))
                sys.exit(1)
            elif (int(gsi['min_provisioned_writes']) >
                    int(gsi['max_provisioned_writes'])):
                print(
                    'min_provisioned_writes ({0}) may not be higher than '
                    'max_provisioned_writes ({1}) for GSI {2}'.format(
                        gsi['min_provisioned_writes'],
                        gsi['max_provisioned_writes'],
                        gsi_name))
                sys.exit(1)


def __check_logging_rules(configuration):
    """ Check that the logging values are proper """
    valid_log_levels = [
        'debug',
        'info',
        'warning',
        'error'
    ]
    if configuration['logging']['log_level'].lower() not in valid_log_levels:
        print('Log level must be one of {0}'.format(
            ', '.join(valid_log_levels)))
        sys.exit(1)


def __check_table_rules(configuration):
    """ Do some basic checks on the configuraion """
    for table_name in configuration['tables']:
        table = configuration['tables'][table_name]
        # Check that increase/decrease units is OK
        valid_units = ['percent', 'units']
        if table['increase_reads_unit'] not in valid_units:
            print('increase-reads-with must be set to either percent or units')
            sys.exit(1)
        if table['decrease_reads_unit'] not in valid_units:
            print('decrease-reads-with must be set to either percent or units')
            sys.exit(1)
        if table['increase_writes_unit'] not in valid_units:
            print(
                'increase-writes-with must be set to either percent or units')
            sys.exit(1)
        if table['decrease_writes_unit'] not in valid_units:
            print(
                'decrease-writes-with must be set to either percent or units')
            sys.exit(1)

        # Check that increase_writes_with is not > 100
        if (table['increase_writes_unit'] == 'percent' and
                table['increase_writes_with'] > 100):

            print(
                'You can not increase the table throughput with more '
                'than 100% at a time. Setting --increase-writes-with to 100.')
            table['increase_writes_with'] = 100

        # Check that increase_reads_with is not > 100
        if (table['increase_reads_unit'] == 'percent' and
                table['increase_reads_with'] > 100):
            print(
                'You can not increase the table throughput with more '
                'than 100% at a time. Setting --increase-reads-with to 100.')
            table['increase_reads_with'] = 100

        # Ensure values > 1 for some important configuration options
        options = [
            'reads_lower_threshold',
            'reads_upper_threshold',
            'increase_reads_with',
            'decrease_reads_with',
            'writes_lower_threshold',
            'writes_upper_threshold',
            'increase_writes_with',
            'decrease_writes_with',
            'min_provisioned_reads',
            'max_provisioned_reads',
            'min_provisioned_writes',
            'max_provisioned_writes'
        ]
        for option in options:
            if table[option] < 1:
                print('{0} may not be lower than 1 for table {1}'.format(
                    option, table_name))
                sys.exit(1)

        if (int(table['min_provisioned_reads']) >
                int(table['max_provisioned_reads'])):
            print(
                'min_provisioned_reads ({0}) may not be higher than '
                'max_provisioned_reads ({1}) for table {2}'.format(
                    table['min_provisioned_reads'],
                    table['max_provisioned_reads'],
                    table_name))
            sys.exit(1)
        elif (int(table['min_provisioned_writes']) >
                int(table['max_provisioned_writes'])):
            print(
                'min_provisioned_writes ({0}) may not be higher than '
                'max_provisioned_writes ({1}) for table {2}'.format(
                    table['min_provisioned_writes'],
                    table['max_provisioned_writes'],
                    table_name))
            sys.exit(1)
