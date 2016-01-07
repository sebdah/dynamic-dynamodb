import os

from dynamic_dynamodb import execute
from dynamic_dynamodb.log_handler import get_logger
from dynamic_dynamodb.config import config_file_parser
from dynamic_dynamodb.config_handler import set_configuration


def handler(event, context):
    set_configuration(config_file_parser.parse(os.path.realpath('dynamic-dynamodb.conf')))
    get_logger().info('Configuration loaded & handler started')

    get_logger().info('Execute handler')
    execute()

    get_logger().info('Handler finished')

