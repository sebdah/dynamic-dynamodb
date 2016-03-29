Dynamic DynamoDB
================

<a href="http://dynamic-dynamodb.readthedocs.org/en/latest/"><img src="https://readthedocs.org/projects/dynamic-dynamodb/badge/?version=latest"></a>

AWS NoSQL database DynamoDB is a great service, but it lacks automated throughput scaling. This is where Dynamic DynamoDB enters the stage. It provides automatic read and write provisioning for DynamoDB.

All you need to do is to tell Dynamic DynamoDB is at which point and how much you want to scale up or down your DynamoDB tables. An example is in place. Let’s say you have way more traffic on your database during sales hours 4pm - 10pm. DynamicDB can monitor the increased throughput on your DynamoDB instance (via CloudWatch) and provision more throughput as needed. When the load is reducing Dynamic DynamoDB will sense that and automatically reduce your provisioning.

See an example of how to configure Dynamic DynamoDB under **Basic usage** or checkout `dynamic-dynamodb --help`.

Features in short
-----------------

- Scale up and down DynamoDB automatically
- Restrict scaling to certain time slots
- Monitor multiple DynamoDB tables at the same time
- Gives you control over how much reads and writes you want to scale up and down with
- Dynamic DynamoDB has support for max and min limits so that you always knows how much money you spend at most and how much capacity you can be guaranteed
- Support for circuit breaker API call. If your service is experiencing disturbances, Dynamic DynamoDB will not scale down your DynamoDB tables

Documentation
-------------

Project documentation is hosted at [dynamic-dynamodb.readthedocs.org](http://dynamic-dynamodb.readthedocs.org/en/latest/index.html).

Basic usage
-----------

This example will configure Dynamic DynamoDB to:

- Scale up your DynamoDB table when the consumed reads 90% of the total provisioned reads
- Scale up your DynamoDB table when the consumed writes 90% of the total provisioned writes
- Scale up your reads with 50%
- Scale up your writes with 40%
- Scale down your DynamoDB table when the consumed reads 30% of the total provisioned reads
- Scale down your DynamoDB table when the consumed writes 40% of the total provisioned writes
- Scale down your reads with 40%
- Scale down your writes with 70%
- Check for changes every 5 minutes

Command:

    dynamic-dynamodb --table-name my-table \
                     --reads-upper-threshold 90 \
                     --reads-lower-threshold 30 \
                     --increase-reads-with 50 \
                     --decrease-reads-with 40 \
                     --writes-upper-threshold 90 \
                     --writes-lower-threshold 40 \
                     --increase-writes-with 40 \
                     --decrease-writes-with 70 \
                     --check-interval 300

Please note that using configuration files instead of command line options will give you even more control over the service.

Installation instructions
-------------------------

The easiest way to install Dynamic DynamoDB is through PyPI:

    pip install dynamic-dynamodb


Required privileges
-------------------

If you want to set up a separate IAM user for Dynamic DynamoDB, then you need to grant the user the following privileges:

* `cloudwatch:GetMetricStatistics`
* `dynamodb:DescribeTable`
* `dynamodb:ListTables`
* `dynamodb:UpdateTable`
* `sns:Publish` (used by the SNS notifications feature)

An example policy could look like this:

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "dynamodb:DescribeTable",
            "dynamodb:ListTables",
            "dynamodb:UpdateTable",
            "cloudwatch:GetMetricStatistics"
          ],
          "Resource": [
            "*"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "sns:Publish"
          ],
          "Resource": [
            "arn:aws:sns:*::dynamic-dynamodb"
          ]
        }
      ]
    }

Community applications
----------------------

There are a few community applications for managing Dynamic DynamoDB.

- [puppet-dynamicdynamodb](https://github.com/mindcandy/puppet-dynamicdynamodb) (Puppet module)
- [elasticDynamoDB](https://github.com/innovia/ElasticDynamoDb) (Wrapper for handling larger planned spikes)
- [Dynamic DynamoDB manager](https://github.com/Mollom/dynamic-dynamodb-manager) (This tool will create your tables, rotate them and update dynamic-dynamodb config file so they are monitored)
- [chef-dynamic-dynamodb](https://github.com/spaceapegames/chef-dynamic-dynamodb) (Chef cookbook - DEPRECATED)

Reporting bugs
--------------

Please help me by providing feedback and bug reports. You can file bugs in the project's [GitHub Issues page](https://github.com/sebdah/dynamic-dynamodb/issues).

Provide as much details as possible to make bug fixing as swift as possible.

Author
------

This project is maintained by [Sebastian Dahlgren](http://www.sebastiandahlgren.se) ([GitHub](https://github.com/sebdah) | [Twitter](https://twitter.com/sebdah) | [LinkedIn](http://www.linkedin.com/in/sebastiandahlgren))

License
-------

APACHE LICENSE 2.0
Copyright 2013-2014 Sebastian Dahlgren

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
