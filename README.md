Dynamic DynamoDB
================

AWS DynamoDB is a great service, but it falls short when it comes to automated throughput scaling. This is where Dynamic DynamoDB enters the stage. It provides automatic read and write provisioning for DynamoDB.

All you need to do is to tell Dynamic DynamoDB at which point and how much you want to scale up or down your DynamoDB. An example is in place. Let’s say you have way more traffic on your database during sales hours 4pm - 10pm. DynamicDB can monitor the increased throughput on your DynamoDB instance (via CloudWatch) and provision more throughput as needed. When the load is reducing Dynamic DynamoDB will sence that and automatically reduce your provisioning.

See an example of how to configure Dynamic DynamoDB under **Basic usage** or checkout `dynamic-dynamodb --help`.

Features in short
-----------------

- Scale up and down DynamoDB automatically
- Restrict scaling to certain time slots
- Gives you control over how much reads and writes you want to scale up and down with
- Dynamic DynamoDB has support for max and min limits so that you always knows how much money you spend at most and how much capacity you can be guaranteed

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

Installation instructions
-------------------------

The easiest way to install Dynamic DynamoDB is through PyPI:

    pip install dynamic-dynamodb

Example configuration file
--------------------------

    [global]
    #aws-access-key-id: AWS_ACCESS_KEY
    #aws-secret-access-key-id: AWS_SECRET_KEY
    region: us-east-1
    check-interval: 300

    [table: my_table]
    # Read provisioning configuration
    reads-upper-threshold: 90
    reads-lower-threshold: 30
    increase-reads-with: 50
    decrease-reads-with: 50
    #min-provisioned-reads: 100
    #max-provisioned-reads: 500

    # Write provisioning configuration
    writes-upper-threshold: 90
    writes-lower-threshold: 30
    increase-writes-with: 50
    decrease-writes-with: 50
    #min-provisioned-writes: 100
    #max-provisioned-writes: 500

    # Maintenance windows (in UTC)
    maintenance-windows: 22:00-23:59,00:00-06:00

Full --help output
------------------

    usage: dynamic_dynamodb [-h] [--dry-run] [--check-interval CHECK_INTERVAL]
                            [--aws-access-key-id AWS_ACCESS_KEY_ID]
                            [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
                            [-r REGION] -t TABLE_NAME
                            [--reads-upper-threshold READS_UPPER_THRESHOLD]
                            [--reads-lower-threshold READS_LOWER_THRESHOLD]
                            [--increase-reads-with INCREASE_READS_WITH]
                            [--decrease-reads-with DECREASE_READS_WITH]
                            [--min-provisioned-reads MIN_PROVISIONED_READS]
                            [--max-provisioned-reads MAX_PROVISIONED_READS]
                            [--writes-upper-threshold WRITES_UPPER_THRESHOLD]
                            [--writes-lower-threshold WRITES_LOWER_THRESHOLD]
                            [--increase-writes-with INCREASE_WRITES_WITH]
                            [--decrease-writes-with DECREASE_WRITES_WITH]
                            [--min-provisioned-writes MIN_PROVISIONED_WRITES]
                            [--max-provisioned-writes MAX_PROVISIONED_WRITES]

    Dynamic DynamoDB - Auto provisioning AWS DynamoDB

    optional arguments:
      -h, --help            show this help message and exit
      --dry-run             Run without making any changes to your DynamoDB table
      --check-interval CHECK_INTERVAL
                            How many seconds should we wait between the checks
                            (default: 300)
      --aws-access-key-id AWS_ACCESS_KEY_ID
                            Override Boto configuration with the following AWS
                            access key
      --aws-secret-access-key AWS_SECRET_ACCESS_KEY
                            Override Boto configuration with the following AWS
                            secret key

    DynamoDB settings:
      -r REGION, --region REGION
                            AWS region to operate in (default: us-east-1
      -t TABLE_NAME, --table-name TABLE_NAME
                            How many percent should we decrease the read units
                            with?

    Read units scaling properties:
      --reads-upper-threshold READS_UPPER_THRESHOLD
                            Scale up the reads with --increase-reads-with percent
                            if the currently consumed read units reaches this many
                            percent (default: 90)
      --reads-lower-threshold READS_LOWER_THRESHOLD
                            Scale down the reads with --decrease-reads-with
                            percent if the currently consumed read units is as low
                            as this percentage (default: 30)
      --increase-reads-with INCREASE_READS_WITH
                            How many percent should we increase the read units
                            with? (default: 50, max: 100)
      --decrease-reads-with DECREASE_READS_WITH
                            How many percent should we decrease the read units
                            with? (default: 50)
      --min-provisioned-reads MIN_PROVISIONED_READS
                            Minimum number of provisioned reads
      --max-provisioned-reads MAX_PROVISIONED_READS
                            Maximum number of provisioned reads

    Write units scaling properties:
      --writes-upper-threshold WRITES_UPPER_THRESHOLD
                            Scale up the writes with --increase-writes-with
                            percent if the currently consumed write units reaches
                            this many percent (default: 90)
      --writes-lower-threshold WRITES_LOWER_THRESHOLD
                            Scale down the writes with --decrease-writes-with
                            percent if the currently consumed write units is as
                            low as this percentage (default: 30)
      --increase-writes-with INCREASE_WRITES_WITH
                            How many percent should we increase the write units
                            with? (default: 50, max: 100)
      --decrease-writes-with DECREASE_WRITES_WITH
                            How many percent should we decrease the write units
                            with? (default: 50)
      --min-provisioned-writes MIN_PROVISIONED_WRITES
                            Minimum number of provisioned writes
      --max-provisioned-writes MAX_PROVISIONED_WRITES
                            Maximum number of provisioned writes

Reporting bugs
--------------

Please help me by providing feedback and bug reports. You can file bugs in the project's [GitHub Issues page](https://github.com/sebdah/dynamic-dynamodb/issues).

Provide as much details as possible to make bug fixing as swift as possible.

Git strategy
------------

This project uses [git-flow](https://github.com/nvie/gitflow) for handling branching and releasing in Git. See the following [blog post](http://nvie.com/posts/a-successful-git-branching-model/) for more details on how it works.

Release information
-------------------

**0.3.0 (2013-03-27)**

This release contains support for configuration files, custom AWS access keys and configurable maintenance windows. The maintenance feature will restrict Dynamic DynamoDB to change your provisioning only during specific time slots.

- [Add support for configuration files (#6)](https://github.com/sebdah/dynamic-dynamodb/issues/6)
- [Configure AWS credentials on command line (#5)](https://github.com/sebdah/dynamic-dynamodb/issues/5)
- [Support for maintenance windows (#1)](https://github.com/sebdah/dynamic-dynamodb/issues/1)

**0.2.0 (2013-03-24)**
- First public release

**0.1.1 (2013-03-24)**
- Initial release

Releasing to PyPI
-----------------

    make release

Author
------

This project is maintained by [Sebastian Dahlgren](http://www.sebastiandahlgren.se) ([GitHub](https://github.com/sebdah) | [Twitter](https://twitter.com/sebdah) | [LinkedIn](www.linkedin.com/in/sebastiandahlgren))
