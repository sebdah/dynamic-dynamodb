# -*- coding: utf-8 -*-
""" Configuration management """
import config_file_parser
import command_line_parser
#from .log_handler import LOGGER as logger


DEFAULT_OPTIONS = {
    # Command line only
    'config': None,
    'daemon': False,
    'dry_run': False,

    # [global]
    'region': 'us-east-1',
    'aws_access_key_id': None,
    'aws_secret_access_key': None,
    'check_interval': 300,

    # [logging]
    'log_file': None,
    'log_level': 'info',

    # [table: x]
    'table_name': None,
    'reads_lower_threshold': 30,
    'reads_upper_threshold': 90,
    'increase_reads_with': 50,
    'decrease_reads_with': 50,
    'writes_lower_threshold': 30,
    'writes_upper_threshold': 90,
    'increase_writes_with': 50,
    'decrease_writes_with': 50,
    'min_provisioned_reads': None,
    'max_provisioned_reads': None,
    'min_provisioned_writes': None,
    'max_provisioned_writes': None,
    'allow_scaling_down_reads_on_0_percent': False,
    'allow_scaling_down_writes_on_0_percent': False,
    'always_decrease_rw_together': False,
    'maintenance_windows': None,
}


def get_configuration():
    """ Get the configuration from command line and config files """
    # This is the dict we will return
    configuration = {}

    # Read the command line options
    cmd_line_options = command_line_parser.parse()

    # If a configuration file is specified, read that as well
    if 'config' in cmd_line_options:
        conf_file_options = config_file_parser.parse(cmd_line_options['config'])

    # Replace any overlapping values so that command line options
    # trumps configuration file options
    for option in DEFAULT_OPTIONS:
        # Get the value from the configuration file
        configuration[option] = conf_file_options.get(
            option, DEFAULT_OPTIONS[option])

        # Get the value from the command line
        if option in cmd_line_options:
            configuration[option] = cmd_line_options.get(option)

    # Check some basic rules
    configuration = check_rules(configuration)

    return configuration


def check_rules(configuration):
    """ Do some basic checks on the configuraion """
    # Check that increase_writes_with is not > 100
    if configuration['increase_writes_with'] > 100:
        print(
            'You can not increase the table throughput with more '
            'than 100% at a time. Setting --increase-writes-with to 100.')
        configuration['increase_writes_with'] = 100

    # Check that increase_reads_with is not > 100
    if configuration['increase_reads_with'] > 100:
        print(
            'You can not increase the table throughput with more '
            'than 100% at a time. Setting --increase-reads-with to 100.')
        configuration['increase_reads_with'] = 100

    return configuration
