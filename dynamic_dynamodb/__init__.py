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
from config_parsers import command_line_parser, config_file_parser

VERSION = '1.0.0'


def main():
    """ Main function called from dynamic-dynamodb """
    # Default configuration
    default_configuration = {
        # Command line only
        'config': None,
        'dry_run': False,

        # [global]
        'aws_region': 'us-east-1',
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
        'min_provisioned_writes': 'apa',
        'max_provisioned_writes': None,
        'allow_scaling_down_reads_on_0_percent': False,
        'allow_scaling_down_writes_on_0_percent': False,
        'always_decrease_rw_together': False,
        'maintenance_windows': None,
    }
    cmd_line_config = command_line_parser.parse(default_configuration)
    if cmd_line_config['config']:
        file_config = config_file_parser.parse(cmd_line_config['config'])


def version():
    """ Returns the version number """
    return VERSION
