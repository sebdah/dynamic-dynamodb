#!/usr/bin/env python
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
import math
import time
import logging
import datetime

from boto import dynamodb
from boto.ec2 import cloudwatch
from boto.exception import DynamoDBResponseError


# pylint: disable=R0902
# pylint: disable=R0913
# pylint: disable=R0914
class DynamicDynamoDB:
    """ Class handling connections and scaling """
    cw_connection = None
    ddb_connection = None

    def __init__(self, region, table_name,
                reads_upper_threshold, reads_lower_threshold,
                increase_reads_with, decrease_reads_with,
                writes_upper_threshold, writes_lower_threshold,
                increase_writes_with, decrease_writes_with,
                min_provisioned_reads=0, max_provisioned_reads=0,
                min_provisioned_writes=0, max_provisioned_writes=0,
                check_interval=300, dry_run=True,
                aws_access_key_id=None, aws_secret_access_key=None,
                maintenance_windows=None):
        """ Constructor setting the basic configuration

        :type region: str
        :param region: AWS region to connect to
        :type table_name: str
        :param table_name: DynamoDB table name to use
        :type reads_upper_threshold: int
        :param reads_upper_threshold: Usage percent when we should scale up
        :type reads_lower_threshold: int
        :param reads_lower_threshold: Usage percent when we should scale down
        :type increase_reads_with: int
        :param increase_reads_with: How many percent to scale up reads with
        :type decrease_reads_with: int
        :param decrease_reads_with: How many percent to scale down reads with
        :type min_provisioned_reads: int
        :param min_provisioned_reads: Minimum number of provisioned reads
        :type max_provisioned_reads: int
        :param max_provisioned_reads: Maximum number of provisioned reads
        :type writes_upper_threshold: int
        :param writes_upper_threshold: Usage percent when we should scale up
        :type writes_lower_threshold: int
        :param writes_lower_threshold: Usage percent when we should scale down
        :type increase_writes_with: int
        :param increase_writes_with: How many percent to scale up writes with
        :type decrease_writes_with: int
        :param decrease_writes_with: How many percent to scale down writes with
        :type min_provisioned_writes: int
        :param min_provisioned_writes: Minimum number of provisioned writes
        :type max_provisioned_writes: int
        :param max_provisioned_writes: Maximum number of provisioned writes
        :type check_interval: int
        :param check_interval: How many seconds to wait between checks
        :type dry_run: bool
        :param dry_run: Set to False if we should make actual changes
        :type aws_access_key_id: str
        :param aws_access_key_id: AWS access key to use
        :type aws_secret_access_key: str
        :param aws_secret_access_key: AWS secret key to use
        :type maintenance_windows: str
        :param maintenance_windows: Example '00:00-01:00,10:00-11:00'
        """
        self.dry_run = dry_run

        #
        # Logging configuration
        #
        self.logger = logging.getLogger('dynamic-dynamodb')
        self.logger.setLevel(logging.DEBUG)
        if self.dry_run:
            stdout_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - dryrun - %(levelname)s - %(message)s')
        else:
            stdout_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(stdout_formatter)
        self.logger.addHandler(console_handler)

        #
        # Handel parameters
        #
        if int(increase_reads_with) > 100:
            self.logger.error(
                'You can not increase the table throughput with more '
                'than 100% at a time. Setting --increase-reads-with to 100.')
            increase_reads_with = 100

        if int(increase_writes_with) > 100:
            self.logger.error(
                'You can not increase the table throughput with more '
                'than 100% at a time. Setting --increase-writes-with to 100.')
            increase_writes_with = 100

        self.region = region
        self.table_name = table_name
        self.reads_upper_threshold = int(reads_upper_threshold)
        self.reads_lower_threshold = int(reads_lower_threshold)
        self.increase_reads_with = int(increase_reads_with)
        self.decrease_reads_with = int(decrease_reads_with)
        self.writes_upper_threshold = int(writes_upper_threshold)
        self.writes_lower_threshold = int(writes_lower_threshold)
        self.increase_writes_with = int(increase_writes_with)
        self.decrease_writes_with = int(decrease_writes_with)
        self.min_provisioned_reads = min_provisioned_reads
        self.max_provisioned_reads = max_provisioned_reads
        self.min_provisioned_writes = min_provisioned_writes
        self.max_provisioned_writes = max_provisioned_writes
        self.check_interval = int(check_interval)
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.maintenance_windows = maintenance_windows

    def run(self):
        """ Public method for starting scaling """
        try:
            while True:
                self.ensure_proper_provisioning()
                self.logger.info('Waiting {0:d}s until checking again'.format(
                    self.check_interval))
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info('Caught termination signal. Exiting.')

    def ensure_proper_provisioning(self):
        """ Public method running once to check the current provisioning

        This method is called by run() in order to check provisioning over time
        """
        read_usage_percent = self._get_consumed_reads_percentage()
        write_usage_percent = self._get_consumed_writes_percentage()

        throughput = {
            'update_needed': False,
            'read_units': self._get_provisioned_read_units(),
            'write_units': self._get_provisioned_write_units()
        }

        # Check if we should update read provisioning
        if read_usage_percent == 0:
            self.logger.info('Scale down is not performed when usage is at 0%')
        elif read_usage_percent >= self.reads_upper_threshold:
            new_value = self._calculate_increase_reads(
                throughput['read_units'],
                self.increase_reads_with)
            throughput['update_needed'] = True
            throughput['read_units'] = new_value

        elif read_usage_percent <= self.reads_lower_threshold:
            new_value = self._calculate_decrease_reads(
                throughput['read_units'],
                self.decrease_reads_with)
            throughput['update_needed'] = True
            throughput['read_units'] = new_value

        # Check if we should update write provisioning
        if write_usage_percent == 0:
            self.logger.info('Scale down is not performed when usage is at 0%')
        elif write_usage_percent >= self.writes_upper_threshold:
            new_value = self._calculate_increase_writes(
                throughput['write_units'],
                self.increase_reads_with)
            throughput['update_needed'] = True
            throughput['write_units'] = new_value
        elif write_usage_percent <= self.writes_lower_threshold:
            new_value = self._calculate_decrease_writes(
                throughput['write_units'],
                self.decrease_reads_with)
            throughput['update_needed'] = True
            throughput['write_units'] = new_value

        # Handle throughput updates
        if throughput['update_needed']:
            self.logger.info(
                'Changing provisioning to {0:d} reads and {1:d} writes'.format(
                    int(throughput['read_units']),
                    int(throughput['write_units'])))
            self._update_throughput(
                throughput['read_units'],
                throughput['write_units'])
        else:
            self.logger.info('No need to change provisioning')

    def _calculate_decrease_reads(self, original_provisioning, percent):
        """ Decrease the original_provisioning with percent %

        :type original_provisioning: int
        :param original_provisioning: The current provisioning
        :type percent: int
        :param percent: How many percent should we decrease with
        :returns: int -- New provisioning value
        """
        decrease = int(float(original_provisioning)*(float(percent)/100))
        new_reads = self._get_provisioned_read_units() - decrease
        if self.min_provisioned_reads > 0:
            if new_reads < self.min_provisioned_reads:
                return self.min_provisioned_reads
        return new_reads

    def _calculate_increase_reads(self, original_provisioning, percent):
        """ Increase the original_provisioning with percent %

        :type original_provisioning: int
        :param original_provisioning: The current provisioning
        :type percent: int
        :param percent: How many percent should we increase with
        :returns: int -- New provisioning value
        """
        increase = int(float(original_provisioning)*(float(percent)/100+1))
        new_reads = self._get_provisioned_read_units() + increase
        if self.max_provisioned_reads > 0:
            if new_reads > self.max_provisioned_reads:
                return self.max_provisioned_reads
        return new_reads

    def _calculate_decrease_writes(self, original_provisioning, percent):
        """ Decrease the original_provisioning with percent %

        :type original_provisioning: int
        :param original_provisioning: The current provisioning
        :type percent: int
        :param percent: How many percent should we decrease with
        :returns: int -- New provisioning value
        """
        decrease = int(float(original_provisioning)*(float(percent)/100))
        new_writes = self._get_provisioned_write_units() - decrease
        if self.min_provisioned_writes > 0:
            if new_writes < self.min_provisioned_writes:
                return self.min_provisioned_writes
        return new_writes

    def _calculate_increase_writes(self, original_provisioning, percent):
        """ Increase the original_provisioning with percent %

        :type original_provisioning: int
        :param original_provisioning: The current provisioning
        :type percent: int
        :param percent: How many percent should we increase with
        :returns: int -- New provisioning value
        """
        increase = int(float(original_provisioning)*(float(percent)/100+1))
        new_writes = self._get_provisioned_write_units() + increase
        if self.max_provisioned_writes > 0:
            if new_writes > self.max_provisioned_writes:
                return self.max_provisioned_writes
        return new_writes

    def _ensure_cloudwatch_connection(self):
        """ Make sure that we have a CloudWatch connection """
        if not self.cw_connection:
            if self.aws_access_key_id and self.aws_secret_access_key:
                self.cw_connection = cloudwatch.connect_to_region(
                    self.region,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key)
            else:
                self.cw_connection = cloudwatch.connect_to_region(self.region)

    def _ensure_dynamodb_connection(self):
        """ Make sure that we have a CloudWatch connection """
        if not self.ddb_connection:
            if self.aws_access_key_id and self.aws_secret_access_key:
                self.ddb_connection = dynamodb.connect_to_region(
                    self.region,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key)
            else:
                self.ddb_connection = dynamodb.connect_to_region(self.region)

    def _get_consumed_reads_percentage(self):
        """ Get the percentage of consumed reads

        :returns: int -- Percentage of consumed reads
        """
        self._ensure_cloudwatch_connection()
        self._ensure_dynamodb_connection()

        metrics = self.cw_connection.get_metric_statistics(
            300,
            datetime.datetime.utcnow()-datetime.timedelta(minutes=15),
            datetime.datetime.utcnow()-datetime.timedelta(minutes=10),
            'ConsumedReadCapacityUnits',
            'AWS/DynamoDB',
            ['Sum'],
            dimensions={'TableName': self.table_name},
            unit='Count')

        if len(metrics) == 0:
            consumed_reads = 0
        else:
            consumed_reads = int(math.ceil(float(metrics[0]['Sum'])/float(300)))

        consumed_reads_percent = int(math.ceil(
            float(consumed_reads) / float(self._get_provisioned_read_units()) * 100))
        self.logger.info('Consumed reads: {0:d}'.format(consumed_reads))
        self.logger.info('Provisioned reads: {0:d}'.format(int(self._get_provisioned_read_units())))
        self.logger.info('Read usage: {0:d}%'.format(consumed_reads_percent))
        return consumed_reads_percent

    def _get_consumed_writes_percentage(self):
        """ Get the percentage of consumed writes

        :returns: int -- Percentage of consumed writes
        """
        self._ensure_cloudwatch_connection()
        self._ensure_dynamodb_connection()

        metrics = self.cw_connection.get_metric_statistics(
            300,
            datetime.datetime.utcnow()-datetime.timedelta(minutes=15),
            datetime.datetime.utcnow()-datetime.timedelta(minutes=10),
            'ConsumedWriteCapacityUnits',
            'AWS/DynamoDB',
            ['Sum'],
            dimensions={'TableName': self.table_name},
            unit='Count')

        if len(metrics) == 0:
            consumed_writes = 0
        else:
            consumed_writes = int(math.ceil(
                float(metrics[0]['Sum'])/float(300)))

        consumed_writes_percent = int(math.ceil(
            float(consumed_writes) / float(self._get_provisioned_write_units()) * 100))
        self.logger.info('Consumed writes: {0:d}'.format(consumed_writes))
        self.logger.info('Provisioned writes: {0:d}'.format(int(self._get_provisioned_write_units())))
        self.logger.info('Write usage: {0:d}%'.format(consumed_writes_percent))
        return consumed_writes_percent

    def _get_provisioned_read_units(self):
        """ Get the provisioned read units for the table

        :returns: int -- Provisioned read units
        """
        self._ensure_dynamodb_connection()
        table = self.ddb_connection.get_table(self.table_name)
        return int(table.read_units)

    def _get_provisioned_write_units(self):
        """ Get the provisioned write units for the table

        :returns: int -- Provisioned write units
        """
        self._ensure_dynamodb_connection()
        table = self.ddb_connection.get_table(self.table_name)
        return int(table.write_units)

    def _is_maintenance_window(self):
        """ Checks that the current time is within the maintenance window

        :returns: bool -- True if within maintenance window
        """
        # If no maintenance windows are defined
        if self.maintenance_windows is None:
            return True

        # Example string '00:00-01:00,10:00-11:00'
        maintenance_windows = []
        for window in self.maintenance_windows.split(','):
            try:
                start, end = window.split('-', 1)
            except ValueError:
                self.logger.error('Malformatted maintenance window')
                return False

            maintenance_windows.append((start, end))

        now = datetime.datetime.utcnow().strftime('%H%M')
        for maintenance_window in maintenance_windows:
            start = ''.join(maintenance_window[0].split(':'))
            end = ''.join(maintenance_window[1].split(':'))
            if now >= start and now <= end:
                return True

        return False

    def _update_throughput(self, read_units, write_units):
        """ Update throughput on the DynamoDB table

        :type read_units: int
        :param read_units: New read unit provisioning
        :type write_units: int
        :param write_units: New write unit provisioning
        """
        self._ensure_dynamodb_connection()
        table = self.ddb_connection.get_table(self.table_name)

        if self.maintenance_windows:
            if not self._is_maintenance_window():
                self.logger.warning(
                    'Current time is outside maintenance window')
                return
            else:
                self.logger.info('Current time is within maintenance window')

        if table.status != 'ACTIVE':
            self.logger.warning(
                'Not performing throughput changes when table '
                'is in {0} state'.format(table.status))

        if not self.dry_run:
            try:
                table.update_throughput(int(read_units), int(write_units))
                self.logger.info('Provisioning updated')
            except DynamoDBResponseError as error:
                dynamodb_error = error.body['__type'].rsplit('#', 1)[1]
                if dynamodb_error == 'LimitExceededException':
                    self.logger.warning(
                        'Scaling limit exeeded. '
                        'The table can only be scaled down twice per day.')
                else:
                    raise
