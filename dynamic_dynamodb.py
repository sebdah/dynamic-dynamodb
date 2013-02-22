#!/usr/bin/env python

"""
Auto-provisioning for AWS DynamoDB tables
"""
import sys
import time
import os.path
import logging
import argparse
import datetime
import ConfigParser
import logging.handlers

from boto import dynamodb
from boto.ec2 import cloudwatch


class DynamicDynamoDB:
    """ Class for a Dynamic DynamoDB worker """
    # Dict storing DynamoDB/CloudWatch connections per AWS region
    dynamodb_connections = {}
    cloudwatch_connections = {}

    def __init__(self, config_file=None):
        """ Constructor

        :param config_file: Custom configuration file to use
        :type config_file: str
        """
        #
        # Logging configuration
        #
        self.logger = logging.getLogger('dynamic-dynamodb')
        self.logger.setLevel(logging.DEBUG)
        stdout_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(stdout_formatter)
        self.logger.addHandler(console_handler)

        #
        # Configuration file management
        #
        if not config_file:
           config_files = [
               os.path.expanduser('~/.dynamic_dynamodb.conf'),
               '/etc/dynamic_dynamodb.conf'
           ]

        self.config = ConfigParser.SafeConfigParser()
        self.config.read(config_files)

    def run(self):
        """ Wrapping the _check method with error handling """
        try:
            while True:
                tables = []
                for table in self.config.sections():
                    if table != 'dynamic-dynamodb-settings':
                        tables.append(table)

                for table in tables:
                    self._check_table(table)

                time.sleep(int(self.config.get(
                    'dynamic-dynamodb-settings',
                    'check-frequency')))

        except KeyboardInterrupt:
            self.logger.info('Caught termination signal. Exiting.')

    def _check_table(self, table_name):
        """ Do the actual checks

        :param table_name: Table name to check
        :type table_name: str
        """
        self.logger.info('Checking table %s', table_name)

        # Connect to DynamoDB
        region = self.config.get(table_name, 'aws-region')
        if region not in self.dynamodb_connections:
            self.logger.debug('Connecting to DynamoDB (%s)', region)
            self.dynamodb_connections[region] = dynamodb.connect_to_region(
                region,
                aws_access_key_id=self.config.get(
                    'dynamic-dynamodb-settings', 'aws-access-key-id'),
                aws_secret_access_key=self.config.get(
                    'dynamic-dynamodb-settings', 'aws-secret-access-key'))

        usage = self._get_usage_percent(table_name)

        #
        # Check write provisioning
        #
        if usage['write_usage'] < self.config.get(table_name, 'writes-scale-down-threshold-percent'):
            self.logger.info('Write consumption is below scale down threshold')
        elif usage['write_usage'] >= self.config.get(table_name, 'writes-scale-up-threshold-percent'):
            self.logger.info('Write consumption is above scale up threshold')
        else:
            self.logger.debug('No need to change write provisioning')

        #
        # Check read provisioning
        #
        if usage['read_usage'] < self.config.get(table_name, 'reads-scale-down-threshold-percent'):
            self.logger.info('Read consumption is below scale down threshold')
        elif usage['read_usage'] >= self.config.get(table_name, 'reads-scale-up-threshold-percent'):
            self.logger.info('Read consumption is above scale up threshold')
        else:
            self.logger.debug('No need to change read provisioning')

    def _get_usage_percent(self, table_name):
        """
        Returns the percentage of the provisioned used of the DynamoDB table

        :param table_name: Table name to check
        :type table_name: str

        :returns: dict -- {'read_usage': 50, 'write_usage': 80}
        """
        # Connect to CloudWatch
        region = self.config.get(table_name, 'aws-region')
        if region not in self.cloudwatch_connections:
            self.logger.debug('Connecting to CloudWatch (%s)', region)
            self.cloudwatch_connections[region] = cloudwatch.connect_to_region(
                region,
                aws_access_key_id=self.config.get(
                    'dynamic-dynamodb-settings', 'aws-access-key-id'),
                aws_secret_access_key=self.config.get(
                    'dynamic-dynamodb-settings', 'aws-secret-access-key'))

        # Calculate the period
        period = int(self.config.get(
            'dynamic-dynamodb-settings', 'check-frequency'))
        if period < 60:
            period = 60

        metrics = self.cloudwatch_connections[region].get_metric_statistics(
            period=60,
            start_time=datetime.datetime.utcnow()-datetime.timedelta(days=6, minutes=5),
            end_time=datetime.datetime.utcnow()-datetime.timedelta(days=6),
            metric_name='ConsumedWriteCapacityUnits',
            namespace='AWS/DynamoDB',
            statistics=['Maximum'],
            dimensions={'TableName': table_name})
        if len(metrics) == 0:
            consumed_writes = 0
        else:
            consumed_writes = int(metrics[0]['Maximum'])
        self.logger.debug(
            'ConsumedWriteCapacityUnits: %i', consumed_writes)

        metrics = self.cloudwatch_connections[region].get_metric_statistics(
            period=60,
            start_time=datetime.datetime.utcnow()-datetime.timedelta(days=6, minutes=5),
            end_time=datetime.datetime.utcnow()-datetime.timedelta(days=6),
            metric_name='ProvisionedWriteCapacityUnits',
            namespace='AWS/DynamoDB',
            statistics=['Maximum'],
            dimensions={'TableName': table_name})
        if len(metrics) == 0:
            provisioned_writes = 0
        else:
            provisioned_writes = int(metrics[0]['Maximum'])
        self.logger.debug(
            'ProvisionedWriteCapacityUnits: %i', provisioned_writes)

        metrics = self.cloudwatch_connections[region].get_metric_statistics(
            period=60,
            start_time=datetime.datetime.utcnow()-datetime.timedelta(minutes=5),
            end_time=datetime.datetime.utcnow()-datetime.timedelta(seconds=10),
            metric_name='ConsumedReadCapacityUnits',
            namespace='AWS/DynamoDB',
            statistics=['Maximum'],
            dimensions={'TableName': table_name})
        if len(metrics) == 0:
            consumed_reads = 0
        else:
            consumed_reads = int(metrics[0]['Maximum'])
        self.logger.debug(
            'ConsumedReadCapacityUnits: %i', consumed_reads)

        metrics = self.cloudwatch_connections[region].get_metric_statistics(
            period=60,
            start_time=datetime.datetime.utcnow()-datetime.timedelta(minutes=5),
            end_time=datetime.datetime.utcnow()-datetime.timedelta(seconds=10),
            metric_name='ProvisionedReadCapacityUnits',
            namespace='AWS/DynamoDB',
            statistics=['Maximum'],
            dimensions={'TableName': table_name})
        if len(metrics) == 0:
            provisioned_reads = 0
        else:
            provisioned_reads = int(metrics[0]['Maximum'])
        self.logger.debug(
            'ProvisionedReadCapacityUnits: %i', provisioned_reads)

        # Calculate percentage
        try:
            write_usage = (consumed_writes / provisioned_writes) * 100
        except ZeroDivisionError:
            write_usage = 0
        try:
            read_usage = (consumed_reads / provisioned_reads) * 100
        except ZeroDivisionError:
            read_usage = 0

        self.logger.debug('Read usage %i%%, write usage: %i%%',
            read_usage, write_usage)

        return {
            'read_usage': read_usage,
            'write_usage': write_usage
        }

def main():
    """ Main function """
    parser = argparse.ArgumentParser(
        description='Auto-provisioning for AWS DynamoDB tables')
    parser.add_argument('-c', '--config-file', type=str, default=None)
    args = parser.parse_args()

    app = DynamicDynamoDB(config_file=args.config_file)
    app.run()

if __name__ == '__main__':
    main()
    sys.exit(0)

sys.exit(1)
