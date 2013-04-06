# -*- coding: utf-8 -*-
""" DynamicDynamoDBDaemon implementation """
import time
from daemon import Daemon


class DynamicDynamoDBDaemon(Daemon):
    """ Daemon class """
    def run(self, *args, **kwargs):
        """ Run the daemon """
        while True:
            time.sleep(1)
