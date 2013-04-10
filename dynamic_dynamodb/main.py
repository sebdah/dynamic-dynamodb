# -*- coding: utf-8 -*-
"""
Dynamic DynamoDB

Auto provisioning functionality for Amazon Web Service DynamoDB tables.


APACHE LICENSE 2.0
Copyright 2013 Sebastian Dahlgren

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys
import logger
import argparse
import ConfigParser
import dynamic_dynamodb

from . import version
from dynamic_dynamodb_daemon import DynamicDynamoDBDaemon


def main():
    """ Main function handling option parsing etc """
    parser = argparse.ArgumentParser(
        description='Dynamic DynamoDB - Auto provisioning AWS DynamoDB')
    parser.add_argument('-c', '--config',
        help='Read configuration from a configuration file')
    parser.add_argument('--dry-run',
        action='store_true',
        help='Run without making any changes to your DynamoDB table')
    parser.add_argument('--daemon',
        help='Run Dynamic DynamoDB as a daemon [start|stop|restart]')
    parser.add_argument('--check-interval',
        type=int,
        default=300,
        help="""How many seconds should we wait between
                the checks (default: 300)""")
    parser.add_argument('--version',
        action='store_true',
        help='Print current version number')
    parser.add_argument('--aws-access-key-id',
        default=None,
        help="Override Boto configuration with the following AWS access key")
    parser.add_argument('--aws-secret-access-key',
        default=None,
        help="Override Boto configuration with the following AWS secret key")
    dynamodb_ag = parser.add_argument_group('DynamoDB settings')
    dynamodb_ag.add_argument('-r', '--region',
        default='us-east-1',
        help='AWS region to operate in (default: us-east-1')
    dynamodb_ag.add_argument('-t', '--table-name',
        help='How many percent should we decrease the read units with?')
    r_scaling_ag = parser.add_argument_group('Read units scaling properties')
    r_scaling_ag.add_argument('--reads-upper-threshold',
        default=90,
        type=int,
        help="""Scale up the reads with --increase-reads-with percent if
                the currently consumed read units reaches this many
                percent (default: 90)""")
    r_scaling_ag.add_argument('--reads-lower-threshold',
        default=30,
        type=int,
        help="""Scale down the reads with --decrease-reads-with percent if the
                currently consumed read units is as low as this
                percentage (default: 30)""")
    r_scaling_ag.add_argument('--increase-reads-with',
        default=50,
        type=int,
        help="""How many percent should we increase the read
                units with? (default: 50, max: 100)""")
    r_scaling_ag.add_argument('--decrease-reads-with',
        default=50,
        type=int,
        help="""How many percent should we decrease the
                read units with? (default: 50)""")
    r_scaling_ag.add_argument('--min-provisioned-reads',
        type=int,
        help="""Minimum number of provisioned reads""")
    r_scaling_ag.add_argument('--max-provisioned-reads',
        type=int,
        help="""Maximum number of provisioned reads""")
    w_scaling_ag = parser.add_argument_group('Write units scaling properties')
    w_scaling_ag.add_argument('--writes-upper-threshold',
        default=90,
        type=int,
        help="""Scale up the writes with --increase-writes-with percent
                if the currently consumed write units reaches this
                many percent (default: 90)""")
    w_scaling_ag.add_argument('--writes-lower-threshold',
        default=30,
        type=int,
        help="""Scale down the writes with --decrease-writes-with percent
                if the currently consumed write units is as low as this
                percentage (default: 30)""")
    w_scaling_ag.add_argument('--increase-writes-with',
        default=50,
        type=int,
        help="""How many percent should we increase the write
                units with? (default: 50, max: 100)""")
    w_scaling_ag.add_argument('--decrease-writes-with',
        default=50,
        type=int,
        help="""How many percent should we decrease the write
                units with? (default: 50)""")
    w_scaling_ag.add_argument('--min-provisioned-writes',
        type=int,
        help="""Minimum number of provisioned writes""")
    w_scaling_ag.add_argument('--max-provisioned-writes',
        type=int,
        help="""Maximum number of provisioned writes""")
    args = parser.parse_args()

    if args.version:
        print 'Dynamic DynamoDB version: {0}'.format(version)
        sys.exit(0)

    if args.aws_access_key_id and not args.aws_secret_access_key:
        print ('Both --aws-access-key-id and --aws-secret-access-key must '
            'be specified.')
        parser.print_help()
        sys.exit(1)

    if args.config:
        config = parse_configuration_file(args.config)
        log_level = get_config_log_level(args.config)
        log_file = get_config_log_file(args.config)
        log_handler = logger.Logger(
            level=log_level,
            log_file=log_file,
            dry_run=args.dry_run)
    else:
        if not args.table_name:
            print 'argument -t/--table-name is required'
            parser.print_help()
            sys.exit(1)

        config = {}

        # Handle command line arguments
        config['region'] = args.region
        config['table-name'] = args.table_name
        config['reads-upper-threshold'] = args.reads_upper_threshold
        config['reads-lower-threshold'] = args.reads_lower_threshold
        config['increase-reads-with'] = args.increase_reads_with
        config['decrease-reads-with'] = args.decrease_reads_with
        config['writes-upper-threshold'] = args.writes_upper_threshold
        config['writes-lower-threshold'] = args.writes_lower_threshold
        config['increase-writes-with'] = args.increase_writes_with
        config['decrease-writes-with'] = args.decrease_writes_with
        config['min-provisioned-reads'] = args.min_provisioned_reads
        config['max-provisioned-reads'] = args.max_provisioned_reads
        config['min-provisioned-writes'] = args.min_provisioned_writes
        config['max-provisioned-writes'] = args.max_provisioned_writes
        config['check-interval'] = args.check_interval
        config['aws-access-key-id'] = args.aws_access_key_id
        config['aws-secret-access-key'] = args.aws_secret_access_key
        config['maintenance-windows'] = None
        log_handler = logger.Logger(dry_run=args.dry_run)

    # Options that can only be seet on command line:
    config['dry-run'] = args.dry_run

    if args.daemon:
        daemon = DynamicDynamoDBDaemon('/tmp/daemon.pid')

        if args.daemon == 'start':
            daemon.start(
                config['region'],
                config['table-name'],
                config['reads-upper-threshold'],
                config['reads-lower-threshold'],
                config['increase-reads-with'],
                config['decrease-reads-with'],
                config['writes-upper-threshold'],
                config['writes-lower-threshold'],
                config['increase-writes-with'],
                config['decrease-writes-with'],
                config['min-provisioned-reads'],
                config['max-provisioned-reads'],
                config['min-provisioned-writes'],
                config['max-provisioned-writes'],
                check_interval=config['check-interval'],
                dry_run=config['dry-run'],
                aws_access_key_id=config['aws-access-key-id'],
                aws_secret_access_key=config['aws-secret-access-key'],
                maintenance_windows=config['maintenance-windows'],
                logger=log_handler)
        elif args.daemon == 'stop':
            daemon.stop()
        elif args.daemon == 'restart':
            daemon.restart()
        else:
            print ('Valid options for --daemon are start, stop and restart')
            parser.print_help()
            sys.exit(1)
    else:
        dynamic_ddb = dynamic_dynamodb.DynamicDynamoDB(
            config['region'],
            config['table-name'],
            config['reads-upper-threshold'],
            config['reads-lower-threshold'],
            config['increase-reads-with'],
            config['decrease-reads-with'],
            config['writes-upper-threshold'],
            config['writes-lower-threshold'],
            config['increase-writes-with'],
            config['decrease-writes-with'],
            config['min-provisioned-reads'],
            config['max-provisioned-reads'],
            config['min-provisioned-writes'],
            config['max-provisioned-writes'],
            check_interval=config['check-interval'],
            dry_run=config['dry-run'],
            aws_access_key_id=config['aws-access-key-id'],
            aws_secret_access_key=config['aws-secret-access-key'],
            maintenance_windows=config['maintenance-windows'],
            logger=log_handler)
        dynamic_ddb.run()


def get_config_log_level(config_path):
    """ Return the configured log level

    :type config_path: str
    :param config_path: Path to the configuration file
    """
    # Read the configuration file
    config_file = ConfigParser.SafeConfigParser()
    config_file.optionxform = lambda option: option
    config_file.read(config_path)

    try:
        return config_file.get('logging', 'log-level')
    except ConfigParser.NoOptionError:
        return 'info'
    except ConfigParser.NoSectionError:
        return 'info'
    return 'info'


def get_config_log_file(config_path):
    """ Return the configured log file

    :type config_path: str
    :param config_path: Path to the configuration file
    """
    # Read the configuration file
    config_file = ConfigParser.SafeConfigParser()
    config_file.optionxform = lambda option: option
    config_file.read(config_path)

    try:
        return config_file.get('logging', 'log-file')
    except ConfigParser.NoOptionError:
        return None
    except ConfigParser.NoSectionError:
        return None
    return None


def parse_configuration_file(config_path):
    """ Parse a configuration file

    :type config_path: str
    :param config_path: Path to the configuration file
    """
    # Read the configuration file
    config_file = ConfigParser.SafeConfigParser()
    config_file.optionxform = lambda option: option
    config_file.read(config_path)

    # Config dict
    config = {}

    # Find the first table definition
    section = None
    for current_section in config_file.sections():
        if current_section.rsplit(':', 1)[0] != 'table':
            continue
        section = current_section
        config['table-name'] = current_section.rsplit(':', 1)[1].strip()
        break

    if not section:
        print 'Could not find a [table: <table_name>] section in {0}'.format(
            config_path)
        sys.exit(1)

    # Global options to consider
    global_options = [
        ('region', True),
        ('check-interval', True),
        ('aws-access-key-id', False),
        ('aws-secret-access-key', False),
    ]

    # Populate the global options
    for option, required in global_options:
        try:
            config[option] = config_file.get('global', option)
        except ConfigParser.NoOptionError:
            if required:
                print 'Missing [global] option "{0}" in {1}'.format(
                    option, config_path)
                sys.exit(1)
            else:
                config[option] = None
        except ConfigParser.NoSectionError:
            print 'Missing section [global] in {0}'.format(config_path)
            sys.exit(1)

    # Table options to consider
    table_options = [
        ('reads-upper-threshold', True),
        ('reads-lower-threshold', True),
        ('increase-reads-with', True),
        ('decrease-reads-with', True),
        ('writes-upper-threshold', True),
        ('writes-lower-threshold', True),
        ('increase-writes-with', True),
        ('decrease-writes-with', True),
        ('min-provisioned-reads', False),
        ('max-provisioned-reads', False),
        ('min-provisioned-writes', False),
        ('max-provisioned-writes', False),
        ('maintenance-windows', False)
    ]

    # Populate the table options
    for option, required in table_options:
        try:
            config[option] = config_file.get(section, option)
        except ConfigParser.NoOptionError:
            if required:
                print 'Missing [{0}] option "{1}" in {2}'.format(
                    section, option, config_path)
                sys.exit(1)
            else:
                config[option] = None

    return config
