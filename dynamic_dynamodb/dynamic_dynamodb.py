# -*- coding: utf-8 -*-

"""
Dynamic DynamoDB

Auto provisioning functionality for Amazon Web Service DynamoDB databases.


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
import sys
import argparse

def main():
    """ Main function handling option parsing etc """
    parser = argparse.ArgumentParser(
        description='Dynamic DynamoDB - Auto provisioning AWS DynamoDB')
    dynamodb_ag = parser.add_argument_group('DynamoDB settings')
    dynamodb_ag.add_argument('-r', '--region',
        required=True,
        help='AWS region to operate in'),
    dynamodb_ag.add_argument('-t', '--table-name',
        required=True,
        help='How many percent should we decrease the read units with?')
    r_scaling_ag = parser.add_argument_group('Read units scaling properties')
    r_scaling_ag.add_argument('--reads-upper-threshold',
        required=True,
        help="""\
Scale up the reads with --increase-reads-with percent if the currently consumed
read units reaches this many percent""")
    r_scaling_ag.add_argument('--reads-lower-threshold',
        required=True,
        help="""\
Scale down the reads with --decrease-reads-with percent if the currently consumed
read units is as low as this percentage""")
    r_scaling_ag.add_argument('--increase-reads-with',
        required=True,
        help='How many percent should we increase the read units with?')
    r_scaling_ag.add_argument('--decrease-reads-with',
        required=True,
        help='How many percent should we decrease the read units with?')
    w_scaling_ag = parser.add_argument_group('Write units scaling properties')
    w_scaling_ag.add_argument('--writes-upper-threshold',
        required=True,
        help="""\
Scale up the writes with --increase-writes-with percent if the currently consumed
write units reaches this many percent""")
    w_scaling_ag.add_argument('--writes-lower-threshold',
        required=True,
        help="""\
Scale down the writes with --decrease-writes-with percent if the currently consumed
write units is as low as this percentage""")
    w_scaling_ag.add_argument('--increase-writes-with',
        required=True,
        help='How many percent should we increase the write units with?')
    w_scaling_ag.add_argument('--decrease-writes-with',
        required=True,
        help='How many percent should we decrease the write units with?')
    args = parser.parse_args()

if __name__ == '__main__':
    main()

sys.exit(0)
