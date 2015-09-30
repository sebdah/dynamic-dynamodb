# -*- coding: utf-8 -*-
""" Command line configuration parser """
import sys
import os.path
import ConfigParser
import ast
from copy import deepcopy

try:
    from collections import OrderedDict as ordereddict
except ImportError:
    import ordereddict

TABLE_CONFIG_OPTIONS = [
    {
        'key': 'enable_reads_autoscaling',
        'option': 'enable-reads-autoscaling',
        'required': False,
        'type': 'bool'
    },
    {
        'key': 'enable_writes_autoscaling',
        'option': 'enable-writes-autoscaling',
        'required': False,
        'type': 'bool'
    },
    {
        'key': 'enable_reads_up_scaling',
        'option': 'enable-reads-up-scaling',
        'required': False,
        'type': 'bool'
    },
    {
        'key': 'enable_reads_down_scaling',
        'option': 'enable-reads-down-scaling',
        'required': False,
        'type': 'bool'
    },
    {
        'key': 'enable_writes_up_scaling',
        'option': 'enable-writes-up-scaling',
        'required': False,
        'type': 'bool'
    },
    {
        'key': 'enable_writes_down_scaling',
        'option': 'enable-writes-down-scaling',
        'required': False,
        'type': 'bool'
    },
    {
        'key': 'reads_lower_threshold',
        'option': 'reads-lower-threshold',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'reads_upper_threshold',
        'option': 'reads-upper-threshold',
        'required': False,
        'type': 'float'
    },
    {
        'key': 'throttled_reads_upper_threshold',
        'option': 'throttled-reads-upper-threshold',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'increase_reads_with',
        'option': 'increase-reads-with',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'decrease_reads_with',
        'option': 'decrease-reads-with',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'increase_reads_unit',
        'option': 'increase-reads-unit',
        'required': True,
        'type': 'str'
    },
    {
        'key': 'decrease_reads_unit',
        'option': 'decrease-reads-unit',
        'required': True,
        'type': 'str'
    },
    {
        'key': 'writes_lower_threshold',
        'option': 'writes-lower-threshold',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'writes_upper_threshold',
        'option': 'writes-upper-threshold',
        'required': False,
        'type': 'float'
    },
    {
        'key': 'throttled_writes_upper_threshold',
        'option': 'throttled-writes-upper-threshold',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'increase_writes_with',
        'option': 'increase-writes-with',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'decrease_writes_with',
        'option': 'decrease-writes-with',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'increase_writes_unit',
        'option': 'increase-writes-unit',
        'required': True,
        'type': 'str'
    },
    {
        'key': 'decrease_writes_unit',
        'option': 'decrease-writes-unit',
        'required': True,
        'type': 'str'
    },
    {
        'key': 'min_provisioned_reads',
        'option': 'min-provisioned-reads',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'max_provisioned_reads',
        'option': 'max-provisioned-reads',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'min_provisioned_writes',
        'option': 'min-provisioned-writes',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'max_provisioned_writes',
        'option': 'max-provisioned-writes',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'maintenance_windows',
        'option': 'maintenance-windows',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'allow_scaling_down_reads_on_0_percent',
        'option': 'allow-scaling-down-reads-on-0-percent',
        'required': False,
        'type': 'bool'
    },
    {
        'key': 'allow_scaling_down_writes_on_0_percent',
        'option': 'allow-scaling-down-writes-on-0-percent',
        'required': False,
        'type': 'bool'
    },
    {
        'key': 'always_decrease_rw_together',
        'option': 'always-decrease-rw-together',
        'required': False,
        'type': 'bool'
    },
    {
        'key': 'sns_topic_arn',
        'option': 'sns-topic-arn',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'sns_message_types',
        'option': 'sns-message-types',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'num_read_checks_before_scale_down',
        'option': 'num-read-checks-before-scale-down',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'num_write_checks_before_scale_down',
        'option': 'num-write-checks-before-scale-down',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'num_write_checks_reset_percent',
        'option': 'num-write-checks-reset-percent',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'num_read_checks_reset_percent',
        'option': 'num-read-checks-reset-percent',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'reads-upper-alarm-threshold',
        'option': 'reads-upper-alarm-threshold',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'reads-lower-alarm-threshold',
        'option': 'reads-lower-alarm-threshold',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'writes-upper-alarm-threshold',
        'option': 'writes-upper-alarm-threshold',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'writes-lower-alarm-threshold',
        'option': 'writes-lower-alarm-threshold',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'lookback_window_start',
        'option': 'lookback-window-start',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'lookback_period',
        'option': 'lookback-period',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'increase_throttled_by_provisioned_reads_unit',
        'option': 'increase-throttled-by-provisioned-reads-unit',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'increase_throttled_by_provisioned_reads_scale',
        'option': 'increase-throttled-by-provisioned-reads-scale',
        'required': False,
        'type': 'dict'
    },
    {
        'key': 'increase_throttled_by_provisioned_writes_unit',
        'option': 'increase-throttled-by-provisioned-writes-unit',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'increase_throttled_by_provisioned_writes_scale',
        'option': 'increase-throttled-by-provisioned-writes-scale',
        'required': False,
        'type': 'dict'
    },
    {
        'key': 'increase_throttled_by_consumed_reads_unit',
        'option': 'increase-throttled-by-consumed-reads-unit',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'increase_throttled_by_consumed_reads_scale',
        'option': 'increase-throttled-by-consumed-reads-scale',
        'required': False,
        'type': 'dict'
    },
    {
        'key': 'increase_throttled_by_consumed_writes_unit',
        'option': 'increase-throttled-by-consumed-writes-unit',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'increase_throttled_by_consumed_writes_scale',
        'option': 'increase-throttled-by-consumed-writes-scale',
        'required': False,
        'type': 'dict'
    },
    {
        'key': 'increase_consumed_reads_unit',
        'option': 'increase-consumed-reads-unit',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'increase_consumed_reads_with',
        'option': 'increase-consumed-reads-with',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'increase_consumed_reads_scale',
        'option': 'increase-consumed-reads-scale',
        'required': False,
        'type': 'dict'
    },
    {
        'key': 'increase_consumed_writes_unit',
        'option': 'increase-consumed-writes-unit',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'increase_consumed_writes_with',
        'option': 'increase-consumed-writes-with',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'increase_consumed_writes_scale',
        'option': 'increase-consumed-writes-scale',
        'required': False,
        'type': 'dict'
    },
    {
        'key': 'decrease_consumed_reads_unit',
        'option': 'decrease-consumed-reads-unit',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'decrease_consumed_reads_with',
        'option': 'decrease-consumed-reads-with',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'decrease_consumed_reads_scale',
        'option': 'decrease-consumed-reads-scale',
        'required': False,
        'type': 'dict'
    },
    {
        'key': 'decrease_consumed_writes_unit',
        'option': 'decrease-consumed-writes-unit',
        'required': False,
        'type': 'str'
    },
    {
        'key': 'decrease_consumed_writes_with',
        'option': 'decrease-consumed-writes-with',
        'required': False,
        'type': 'int'
    },
    {
        'key': 'decrease_consumed_writes_scale',
        'option': 'decrease-consumed-writes-scale',
        'required': False,
        'type': 'dict'
    }
]


def __parse_options(config_file, section, options):
    """ Parse the section options

    :type config_file: ConfigParser object
    :param config_file: The config file object to use
    :type section: str
    :param section: Which section to read in the configuration file
    :type options: list of dicts
    :param options:
        A list of options to parse. Example list::
        [{
            'key': 'aws_access_key_id',
            'option': 'aws-access-key-id',
            'required': False,
            'type': str
        }]
    :returns: dict
    """
    configuration = {}
    for option in options:
        try:
            if option.get('type') == 'str':
                configuration[option.get('key')] = \
                    config_file.get(section, option.get('option'))
            elif option.get('type') == 'int':
                try:
                    configuration[option.get('key')] = \
                        config_file.getint(section, option.get('option'))
                except ValueError:
                    print('Error: Expected an integer value for {0}'.format(
                        option.get('option')))
                    sys.exit(1)
            elif option.get('type') == 'float':
                try:
                    configuration[option.get('key')] = \
                        config_file.getfloat(section, option.get('option'))
                except ValueError:
                    print('Error: Expected an float value for {0}'.format(
                        option.get('option')))
                    sys.exit(1)
            elif option.get('type') == 'bool':
                try:
                    configuration[option.get('key')] = \
                        config_file.getboolean(section, option.get('option'))
                except ValueError:
                    print('Error: Expected an boolean value for {0}'.format(
                        option.get('option')))
                    sys.exit(1)
            elif option.get('type') == 'dict':
                configuration[option.get('key')] = \
                    ast.literal_eval(
                        config_file.get(section, option.get('option')))
            else:
                configuration[option.get('key')] = \
                    config_file.get(section, option.get('option'))
        except ConfigParser.NoOptionError:
            if option.get('required'):
                print('Missing [{0}] option "{1}" in configuration'.format(
                    section, option.get('option')))
                sys.exit(1)

    return configuration


def parse(config_path):
    """ Parse the configuration file

    :type config_path: str
    :param config_path: Path to the configuration file
    """
    config_path = os.path.expanduser(config_path)

    # Read the configuration file
    config_file = ConfigParser.RawConfigParser()
    config_file.optionxform = lambda option: option
    config_file.read(config_path)

    #
    # Handle [global]
    #
    if 'global' in config_file.sections():
        global_config = __parse_options(
            config_file,
            'global',
            [
                {
                    'key': 'aws_access_key_id',
                    'option': 'aws-access-key-id',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'aws_secret_access_key',
                    'option': 'aws-secret-access-key-id',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'region',
                    'option': 'region',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'check_interval',
                    'option': 'check-interval',
                    'required': False,
                    'type': 'int'
                },
                {
                    'key': 'circuit_breaker_url',
                    'option': 'circuit-breaker-url',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'circuit_breaker_timeout',
                    'option': 'circuit-breaker-timeout',
                    'required': False,
                    'type': 'float'
                },
            ])

    #
    # Handle [logging]
    #
    if 'logging' in config_file.sections():
        logging_config = __parse_options(
            config_file,
            'logging',
            [
                {
                    'key': 'log_level',
                    'option': 'log-level',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'log_file',
                    'option': 'log-file',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'log_config_file',
                    'option': 'log-config-file',
                    'required': False,
                    'type': 'str'
                }
            ])

    if 'default_options' in config_file.sections():
        # nothing is required in defaults, so we set required to False
        default_config_options = deepcopy(TABLE_CONFIG_OPTIONS)
        for item in default_config_options:
            item['required'] = False
        default_options = __parse_options(
            config_file, 'default_options', default_config_options)
        # if we've got a default set required to be false for table parsing
        for item in TABLE_CONFIG_OPTIONS:
            if item['key'] in default_options:
                item['required'] = False
    else:
        default_options = {}

    #
    # Handle [table: ]
    #
    table_config = {'tables': ordereddict()}

    # Find the first table definition
    found_table = False
    for current_section in config_file.sections():
        if current_section.rsplit(':', 1)[0] != 'table':
            continue

        found_table = True
        current_table_name = current_section.rsplit(':', 1)[1].strip()
        table_config['tables'][current_table_name] = \
            dict(default_options.items() + __parse_options(
                config_file, current_section, TABLE_CONFIG_OPTIONS).items())

    if not found_table:
        print('Could not find a [table: <table_name>] section in {0}'.format(
            config_path))
        sys.exit(1)

    # Find gsi definitions - this allows gsi's to be defined before the table
    # definitions we don't worry about parsing everything twice here
    for current_section in config_file.sections():
        try:
            header1, gsi_key, header2, table_key = current_section.split(' ')
        except ValueError:
            continue

        if header1 != 'gsi:':
            continue

        if table_key not in table_config['tables']:
            print('No table configuration matching {0} found.'.format(
                table_key))
            sys.exit(1)

        if 'gsis' not in table_config['tables'][table_key]:
            table_config['tables'][table_key]['gsis'] = {}

        table_config['tables'][table_key]['gsis'][gsi_key] = \
            ordereddict(default_options.items() + __parse_options(
                config_file, current_section, TABLE_CONFIG_OPTIONS).items())

    return ordereddict(
        global_config.items() +
        logging_config.items() +
        table_config.items())
