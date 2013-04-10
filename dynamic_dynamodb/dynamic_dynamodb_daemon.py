# -*- coding: utf-8 -*-
""" DynamicDynamoDBDaemon implementation """
from daemon import Daemon
from dynamic_dynamodb import DynamicDynamoDB


class DynamicDynamoDBDaemon(Daemon):
    """ Daemon class """
    def run(self, *args, **kwargs):
        """ Run the daemon """
        dynamic_dynamodb = DynamicDynamoDB(*args, **kwargs)
        dynamic_dynamodb.run()
