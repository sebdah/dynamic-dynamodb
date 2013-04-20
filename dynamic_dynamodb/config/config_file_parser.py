""" Command line configuration parser """
import sys
import os.path
import ConfigParser


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
                configuration[option.get('key')] = \
                    config_file.getint(section, option.get('option'))
            elif option.get('type') == 'float':
                configuration[option.get('key')] = \
                    config_file.getfloat(section, option.get('option'))
            elif option.get('type') == 'bool':
                configuration[option.get('key')] = \
                    config_file.getboolean(section, option.get('option'))
            else:
                configuration[option.get('key')] = \
                    config_file.get(section, option.get('option'))
        except ConfigParser.NoOptionError:
            if option.get('required'):
                print 'Missing [{0}] option "{1}" in configuration'.format(
                    section, option.get('option'))
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
                }
            ])

    #
    # Handle [table: ]
    #
    table_config = { 'tables': {} }

    # Find the first table definition
    found_table = False
    for current_section in config_file.sections():
        if current_section.rsplit(':', 1)[0] != 'table':
            continue

        found_table = True
        current_table_name = current_section.rsplit(':', 1)[1].strip()
        table_config['tables'][current_table_name] = __parse_options(
            config_file,
            current_section,
            [
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
            ])

    if not found_table:
        print 'Could not find a [table: <table_name>] section in {0}'.format(
            config_path)
        sys.exit(1)

    return dict(
        global_config.items() +
        logging_config.items() +
        table_config.items())

