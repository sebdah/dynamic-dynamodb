#!/usr/bin/env python

"""
Auto-provisioning for AWS DynamoDB tables
"""
import logging
import logging.handlers
from daemon import runner


class DynamicDynamoDB:
    def __init__(self):
        #
        # Daemon configuration
        #
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/foo.pid'
        self.pidfile_timeout = 5

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
        #config_files = [
        #    os.path.expanduser('~/.dynamic_dynamodb.conf'),
        #    '/etc/dynamic_dynamodb.conf'
        #]

    def run(self):
        while True:
            self.logger.warning('Running too fast')

app = DynamicDynamoDB()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.run()
