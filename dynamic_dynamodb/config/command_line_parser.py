# -*- coding: utf-8 -*-
""" Command line configuration parser """
import sys
import os.path
import argparse
import ConfigParser


def parse():
    """ Parse command line options """
    parser = argparse.ArgumentParser(
        description='Dynamic DynamoDB - Auto provisioning AWS DynamoDB')
    parser.add_argument(
        '-c', '--config',
        help='Read configuration from a configuration file')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without making any changes to your DynamoDB table')
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Run once and then exit Dynamic DynamoDB, instead of looping')
    parser.add_argument(
        '--check-interval',
        type=int,
        help="""How many seconds should we wait between
                the checks (default: 300)""")
    parser.add_argument(
        '--log-file',
        help='Send output to the given log file')
    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warning', 'error'],
        help='Log level to use (default: info)')
    parser.add_argument(
        '--log-config-file',
        help=(
            'Use a custom Python logging configuration file. Overrides both '
            '--log-level and --log-file.'
        ))
    parser.add_argument(
        '--version',
        action='store_true',
        help='Print current version number')
    parser.add_argument(
        '--aws-access-key-id',
        help="Override Boto configuration with the following AWS access key")
    parser.add_argument(
        '--aws-secret-access-key',
        help="Override Boto configuration with the following AWS secret key")
    daemon_ag = parser.add_argument_group('Daemon options')
    daemon_ag.add_argument(
        '--daemon',
        help=(
            'Run Dynamic DynamoDB in daemon mode. Valid modes are '
            '[start|stop|restart|foreground]'))
    daemon_ag.add_argument(
        '--instance',
        default='default',
        help=(
            'Name of the Dynamic DynamoDB instance. '
            'Used to run multiple instances of Dynamic DynamoDB. '
            'Give each instance a unique name and control them separately '
            'with the --daemon flag. (default: default)'))
    daemon_ag.add_argument(
        '--pid-file-dir',
        default='/tmp',
        help='Directory where pid file is located in. Defaults to /tmp')
    dynamodb_ag = parser.add_argument_group('DynamoDB options')
    dynamodb_ag.add_argument(
        '-r', '--region',
        help='AWS region to operate in (default: us-east-1')
    dynamodb_ag.add_argument(
        '-t', '--table-name',
        help=(
            'Table(s) to target. '
            'The name is treated as a regular expression. '
            'E.g. "^my_table.*$" or "my_table"'))
    r_scaling_ag = parser.add_argument_group('Read units scaling properties')
    r_scaling_ag.add_argument(
        '--reads-upper-threshold',
        type=int,
        help="""Scale up the reads with --increase-reads-with if
                the currently consumed read units reaches this many
                percent (default: 90)""")
    r_scaling_ag.add_argument(
        '--throttled-reads-upper-threshold',
        type=int,
        help="""Scale up the reads with --increase-reads-with if
                the count of throttled read events exceeds this
                count (default: 0)""")
    r_scaling_ag.add_argument(
        '--reads-lower-threshold',
        type=int,
        help="""Scale down the reads with --decrease-reads-with if the
                currently consumed read units is as low as this
                percentage (default: 30)""")
    r_scaling_ag.add_argument(
        '--increase-reads-with',
        type=int,
        help="""How much should we increase the read units with?
                (default: 50, max: 100 if --increase-reads-unit = percent)""")
    r_scaling_ag.add_argument(
        '--decrease-reads-with',
        type=int,
        help="""How much should we decrease the read units with?
                (default: 50)""")
    r_scaling_ag.add_argument(
        '--increase-reads-unit',
        type=str,
        help='Do you want to scale in percent or units? (default: percent)')
    r_scaling_ag.add_argument(
        '--decrease-reads-unit',
        type=str,
        help='Do you want to scale in percent or units? (default: percent)')
    r_scaling_ag.add_argument(
        '--min-provisioned-reads',
        type=int,
        help="""Minimum number of provisioned reads""")
    r_scaling_ag.add_argument(
        '--max-provisioned-reads',
        type=int,
        help="""Maximum number of provisioned reads""")
    r_scaling_ag.add_argument(
        '--num-read-checks-before-scale-down',
        type=int,
        help="""Number of consecutive checks that must meet criteria
            before a scale down event occurs""")
    r_scaling_ag.add_argument(
        '--num-read-checks-reset-percent',
        type=int,
        help="""Percentage Value that will cause the num_read_checks_before
            scale_down var to reset back to 0""")
    w_scaling_ag = parser.add_argument_group('Write units scaling properties')
    w_scaling_ag.add_argument(
        '--writes-upper-threshold',
        type=int,
        help="""Scale up the writes with --increase-writes-with
                if the currently consumed write units reaches this
                many percent (default: 90)""")
    w_scaling_ag.add_argument(
        '--throttled-writes-upper-threshold',
        type=int,
        help="""Scale up the reads with --increase-writes-with if
                the count of throttled write events exceeds this
                count (default: 0)""")
    w_scaling_ag.add_argument(
        '--writes-lower-threshold',
        type=int,
        help="""Scale down the writes with --decrease-writes-with
                if the currently consumed write units is as low as this
                percentage (default: 30)""")
    w_scaling_ag.add_argument(
        '--increase-writes-with',
        type=int,
        help="""How much should we increase the write units with?
                (default: 50,
                max: 100 if --increase-writes-unit = 'percent')""")
    w_scaling_ag.add_argument(
        '--decrease-writes-with',
        type=int,
        help="""How much should we decrease the write units with?
                (default: 50)""")
    w_scaling_ag.add_argument(
        '--increase-writes-unit',
        type=str,
        help='Do you want to scale in percent or units? (default: percent)')
    w_scaling_ag.add_argument(
        '--decrease-writes-unit',
        type=str,
        help='Do you want to scale in percent or units? (default: percent)')
    w_scaling_ag.add_argument(
        '--min-provisioned-writes',
        type=int,
        help="""Minimum number of provisioned writes""")
    w_scaling_ag.add_argument(
        '--max-provisioned-writes',
        type=int,
        help="""Maximum number of provisioned writes""")
    w_scaling_ag.add_argument(
        '--num-write-checks-before-scale-down',
        type=int,
        help="""Number of consecutive checks that must meet criteria
            before a scale down event occurs""")
    w_scaling_ag.add_argument(
        '--num-write-checks-reset-percent',
        type=int,
        help="""Percentage Value that will cause the num_write_checks_before
            scale_down var to reset back to 0""")
    args = parser.parse_args()

    # Print the version and quit
    if args.version:
        # Read the dynamic-dynamodb.conf configuration file
        internal_config_file = ConfigParser.RawConfigParser()
        internal_config_file.optionxform = lambda option: option
        internal_config_file.read(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), '../dynamic-dynamodb.conf')))

        print 'Dynamic DynamoDB version: {0}'.format(
            internal_config_file.get('general', 'version'))
        sys.exit(0)

    # Replace any new values in the configuration
    configuration = {}
    for arg in args.__dict__:
        if args.__dict__.get(arg) is not None:
            configuration[arg] = args.__dict__.get(arg)

    return configuration
