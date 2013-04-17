# -*- coding: utf-8 -*-
"""
Logging management for Dynamic DynamoDB

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
import os.path
import logging

import config_handler


class LogHandler:
    """ Logging class """
    def __init__(self, name='dynamic-dynamodb', level='info',
                 log_file=None, dry_run=False):
        """ Instanciate the logger

        :type name: str
        :param name: Logger name
        :type level: str
        :param level: Log level [debug|info|warning|error]
        :type log_file: str
        :param log_file: Path to log file (if any)
        :type dry_run: bool
        :param dry_run: Add dry-run to the output
        """
        # Set up the logger
        self.logger = logging.getLogger(name)
        if level.lower() == 'debug':
            self.logger.setLevel(logging.DEBUG)
        elif level.lower() == 'info':
            self.logger.setLevel(logging.INFO)
        elif level.lower() == 'warning':
            self.logger.setLevel(logging.WARNING)
        elif level.lower() == 'error':
            self.logger.setLevel(logging.ERROR)
        else:
            self.logger.setLevel(logging.INFO)

        # Formatting
        if dry_run:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - dryrun - %(message)s')
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            file_handler = logging.FileHandler(os.path.expanduser(log_file))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, *args, **kwargs):
        """ Log on debug level """
        self.logger.debug(*args, **kwargs)

    def error(self, *args, **kwargs):
        """ Log on error level """
        self.logger.error(*args, **kwargs)

    def info(self, *args, **kwargs):
        """ Log on info level """
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """ Log on warning level """
        self.logger.warning(*args, **kwargs)


def __get_logger():
    """ Returns the logger """
    # Instanciate a new logger
    if config_handler.get_logging_option('log_file'):
        logger = LogHandler(
            level=config_handler.get_logging_option('log_level'),
            log_file=config_handler.get_logging_option('log_file'),
            dry_run=config_handler.get_global_option('dry_run'))
    else:
        logger = LogHandler(
            level=config_handler.get_logging_option('log_level'),
            dry_run=config_handler.get_global_option('dry_run'))

    return logger


LOGGER = __get_logger()
