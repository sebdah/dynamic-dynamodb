Dynamic DynamoDB
================

Amazon Web Services DynamoDB hosted NoSQL solition, but it falls short when it comes to automatic scaling. This is where Dynamic DynamoDB enters the stage. It provides automatic read and write provisioning for DynamoDB.

All you need to do is to tell Dynamic DynamoDB at which point and how much you want to scale up or down your DynamoDB. For example, if the consumed read capacity reaches 90%, it might be a good idea to scale up the read provisioning slightly to meet the flood of requests to your service.

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

Full --help output
------------------

    usage: dynamic-dynamodb [-h] [--dry-run] [--check-interval CHECK_INTERVAL]
                            [-r REGION] -t TABLE_NAME
                            [--reads-upper-threshold READS_UPPER_THRESHOLD]
                            [--reads-lower-threshold READS_LOWER_THRESHOLD]
                            [--increase-reads-with INCREASE_READS_WITH]
                            [--decrease-reads-with DECREASE_READS_WITH]
                            [--writes-upper-threshold WRITES_UPPER_THRESHOLD]
                            [--writes-lower-threshold WRITES_LOWER_THRESHOLD]
                            [--increase-writes-with INCREASE_WRITES_WITH]
                            [--decrease-writes-with DECREASE_WRITES_WITH]

    Dynamic DynamoDB - Auto provisioning AWS DynamoDB

    optional arguments:
      -h, --help            show this help message and exit
      --dry-run             Run without making any changes to your DynamoDB
                            database
      --check-interval CHECK_INTERVAL
                            How many seconds should we wait between the checks
                            (default: 300)

    DynamoDB settings:
      -r REGION, --region REGION
                            AWS region to operate in
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
                            with? (default: 50)
      --decrease-reads-with DECREASE_READS_WITH
                            How many percent should we decrease the read units
                            with? (default: 50)

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
                            with? (default: 50)
      --decrease-writes-with DECREASE_WRITES_WITH
                            How many percent should we decrease the write units
                            with? (default: 50)

Reporting bugs
--------------

Please help me by providing feedback and bug reports. You can file bugs in the project's [GitHub Issues page](https://github.com/sebdah/dynamic-dynamodb/issues).

Provide as much details as possible to make bug fixing as swift as possible.

Git strategy
------------

This project uses [git-flow](https://github.com/nvie/gitflow) for handling branching and releasing in Git. See the following [blog post](http://nvie.com/posts/a-successful-git-branching-model/) for more details on how it works.

Release information
-------------------

**0.1.4 (2013-03-24)**
- Initial release

Releasing to PyPI
-----------------

    make release

Author
------

This project is maintained by [Sebastian Dahlgren](http://www.sebastiandahlgren.se) ([GitHub](https://github.com/sebdah) | [Twitter](https://twitter.com/sebdah) | [LinkedIn](www.linkedin.com/in/sebastiandahlgren))
