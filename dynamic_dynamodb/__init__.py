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
import config
import log_handler

VERSION = '1.0.0'


def main():
    """ Main function called from dynamic-dynamodb """
    # Get the configuration
    configuration = config.get_configuration()

    # Instanciate a new logger
    if configuration['log_file']:
        logger = log_handler.LogHandler(
            level=configuration['log_level'],
            log_file=configuration['log_file'],
            dry_run=configuration['dry_run'])
    else:
        logger = log_handler.LogHandler(
            level=configuration['log_level'],
            dry_run=configuration['dry_run'])


def version():
    """ Returns the version number """
    return VERSION

