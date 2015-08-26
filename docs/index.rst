.. toctree::
    :hidden:
    :maxdepth: 3

    installation
    configuration_options
    example_configuration
    command_line_options
    granular_scaling
    iam_permissions
    cloudformation_template
    release_notes
    bug_reporting
    license

Dynamic DynamoDB
================

AWS DynamoDB is a great service, but it lacks support for automated throughput scaling. This is where Dynamic DynamoDB enters the stage. It provides automatic read and write provisioning for DynamoDB.

Features in short
-----------------

- Scale up and down DynamoDB automatically
- Restrict scaling to certain time slots
- Monitor multiple DynamoDB tables at the same time
- Gives you control over how much reads and writes you want to scale up and down with
- Dynamic DynamoDB has support for max and min limits so that you always knows how much money you spend at most and how much capacity you can be guaranteed
- Get notifications when your table provisioning changes via e-mail, HTTP, SQS etc (via AWS SNS)
- Support for circuit breaker API call. If your service is experiencing disturbances, Dynamic DynamoDB will not scale down your DynamoDB tables

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
::

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

Author
------

This project is maintained by `Sebastian Dahlgren <http://www.sebastiandahlgren.se>`_ (`GitHub <https://github.com/sebdah>`_ | `Twitter <https://twitter.com/sebdah>`_ | `LinkedIn <http://www.linkedin.com/in/sebastiandahlgren>`_)
