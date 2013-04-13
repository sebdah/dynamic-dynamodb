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
from default_configuration import CONFIGURATION

VERSION = '1.0.0'


def main():
    """ Main function called from dynamic-dynamodb """
    # Read the command line options
    cmd_line_config = command_line_parser.parse(CONFIGURATION)

    # If a configuration file is specified, read that as well
    if cmd_line_config['config']:
        file_config = config_file_parser.parse(cmd_line_config['config'])


def version():
    """ Returns the version number """
    return VERSION
