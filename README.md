# Dynamic DynamoDB

AWS DynamoDB is a great service, but it falls short when it comes to automated throughput scaling. This is where Dynamic DynamoDB enters the stage. It provides automatic read and write provisioning for DynamoDB.

All you need to do is to tell Dynamic DynamoDB at which point and how much you want to scale up or down your DynamoDB. An example is in place. Let’s say you have way more traffic on your database during sales hours 4pm - 10pm. DynamicDB can monitor the increased throughput on your DynamoDB instance (via CloudWatch) and provision more throughput as needed. When the load is reducing Dynamic DynamoDB will sence that and automatically reduce your provisioning.

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


Reporting bugs
--------------

Please help me by providing feedback and bug reports. You can file bugs in the project's [GitHub Issues page](https://github.com/sebdah/dynamic-dynamodb/issues).

Provide as much details as possible to make bug fixing as swift as possible.

Git strategy
------------

This project uses [git-flow](https://github.com/nvie/gitflow) for handling branching and releasing in Git. See the following [blog post](http://nvie.com/posts/a-successful-git-branching-model/) for more details on how it works.

Release information
-------------------

**1.6.0 (2013-11-21)**

- Documented project in Sphinx - [http://dynamic-dynamodb.readthedocs.org](http://dynamic-dynamodb.readthedocs.org)
- Fixed [Failure on non-matching regular expressions #69](https://github.com/sebdah/dynamic-dynamodb/issues/69)
- Fixed bug [cleanup logs in case of noop updates #71](https://github.com/sebdah/dynamic-dynamodb/issues/71) - Thanks [@tmorgan](https://github.com/tmorgan)

**1.5.8 (2013-10-18)**

- Fixed bug [Under some circumstances Dynamic DynamoDB crashes when table is deleted #68](https://github.com/sebdah/dynamic-dynamodb/issues/68)

**1.5.7 (2013-10-17)**

- Closed [Support for running dynamic-dynamodb with supervisord #66](https://github.com/sebdah/dynamic-dynamodb/issues/66) with [Pull Request #67](https://github.com/sebdah/dynamic-dynamodb/pull/67). Thanks @pragnesh!

**1.5.6 (2013-10-06)**

- [Fixed issue where DDB didn't support increasing capacity two times #65](https://github.com/sebdah/dynamic-dynamodb/pull/65)

**1.5.5 (2013-08-31)**

- [Change log level of informational message](https://github.com/sebdah/dynamic-dynamodb/issues/62)

**1.5.4 (2013-08-29)**

- [Added missing `key_name` parameter](https://github.com/sebdah/dynamic-dynamodb/issues/60)

**1.5.3 (2013-08-27)**

- [Added missing sleep statement fixes](https://github.com/sebdah/dynamic-dynamodb/issues/58)

**1.5.2 (2013-08-27)**

- [Issue with `always-decrease-rw-together` option](https://github.com/sebdah/dynamic-dynamodb/issues/55)
- [ListTables permission required](https://github.com/sebdah/dynamic-dynamodb/issues/57)

The AWS `ListTables` permission is no longer a hard requirement. It's only needed if you're using regular expressions to configure your DynamoDB tables.

**1.5.1 (2013-08-22)**

- [No module named core](https://github.com/sebdah/dynamic-dynamodb/issues/53) (fixed by [#54](https://github.com/sebdah/dynamic-dynamodb/pull/54))

Fixed bug in the 1.5.0 release.

**1.5.0 (2013-08-22)**

- [Support for regular expressions in config](https://github.com/sebdah/dynamic-dynamodb/issues/52)

Thanks [@pragnesh](https://github.com/pragnesh) for adding this feature!

**1.4.0 (2013-08-14)**

- [Retrying failed DynamoDB connections](https://github.com/sebdah/dynamic-dynamodb/issues/51)

**1.3.6 (2013-07-21)**

- [int() argument must be a string or a number, not 'NoneType' (#50)](https://github.com/sebdah/dynamic-dynamodb/issues/50)

**1.3.5 (2013-06-17)**

- [increase_writes_unit parameter is used while it should be decrease_writes_unit (#47)](https://github.com/sebdah/dynamic-dynamodb/issues/47)

**1.3.4 (2013-06-13)**

- [An attempt to update provisioning is made even if the requested values are equal to the tables current values (#46)](https://github.com/sebdah/dynamic-dynamodb/issues/46)

**1.3.3 (2013-06-08)**

- [Increasing to a minimum provisioned throughput value doesn't take into account the current table's throughput (#45)](https://github.com/sebdah/dynamic-dynamodb/issues/45)
- [dynamic-dynamodb --version causes AttributeError in cli (#44)](https://github.com/sebdah/dynamic-dynamodb/issues/44)

**1.3.2 (2013-05-14)**

- [increase_reads_in_percent calculations are incorrect (#40)](https://github.com/sebdah/dynamic-dynamodb/issues/40)

**1.3.1 (2013-05-10)**

- [Fix Python 2.6 support (#39)](https://github.com/sebdah/dynamic-dynamodb/issues/39)

**1.3.0 (2013-05-01)**

This Dynamic DynamoDB release makes it possible to use multiple Dynamic DynamoDB instances in parallel in daemon mode. Simply use the `--instance` flag to separate the difference instances with a unique name. Then control them as usual with the `--daemon` flag.

- [Allow to run multiple instances in parallel (#37)](https://github.com/sebdah/dynamic-dynamodb/issues/37)

**1.2.5 (2013-04-29)**

- [Handle ResourceInUseException better (#36)](https://github.com/sebdah/dynamic-dynamodb/issues/36)
- [Add --log-level option to command line (#34)](https://github.com/sebdah/dynamic-dynamodb/issues/34)

**1.2.4 (2013-04-26)**

- [Mix up between percent and units (#35)](https://github.com/sebdah/dynamic-dynamodb/issues/35)
- Broken build fixed

**1.2.0 (2013-04-20)**

- [Add support for dead-man's-switch API call (#25)](https://github.com/sebdah/dynamic-dynamodb/issues/25)

**1.1.0 (2013-04-17)**

- [Update provisioning in units not just percentage (#22)](https://github.com/sebdah/dynamic-dynamodb/issues/22)
- [Increase in percent does not add to current provisioning properly (#33)](https://github.com/sebdah/dynamic-dynamodb/issues/33)
- [Enhance configuration option validation (#32)](https://github.com/sebdah/dynamic-dynamodb/issues/32)

**1.0.1 (2013-04-17)**

- Minor fix: Ugly output removed

**1.0.0 (2013-04-16)**

The 1.0.0 release is a leap forward when it comes to module structure and extendability. Please remember that this is still released in beta in PyPI, so all bug reports are very welcome. File any odd behavior or bugs in [GitHub Issues](https://github.com/sebdah/dynamic-dynamodb/issues).

- [Restructure the Dynamic DynamoDB code base (#30)](https://github.com/sebdah/dynamic-dynamodb/issues/30)
- [Support multiple tables in one configuration file (#19)](https://github.com/sebdah/dynamic-dynamodb/issues/19)
- [Change pid file name (#31)](https://github.com/sebdah/dynamic-dynamodb/issues/31)
- [Handle combinations of configuration file and command line options better (#24)](https://github.com/sebdah/dynamic-dynamodb/issues/24)

**0.5.0 (2013-04-12)**

- [Add --log-file command line option (#20)](https://github.com/sebdah/dynamic-dynamodb/issues/20)
- [Allow scale down at 0% consumed count (#17)](https://github.com/sebdah/dynamic-dynamodb/issues/17)
- ["only downscale reads AND writes" option would be useful (#23)](https://github.com/sebdah/dynamic-dynamodb/issues/23)

**0.4.2 (2013-04-11)**

- [Unhandled exception: ValidationException (#28)](https://github.com/sebdah/dynamic-dynamodb/issues/28)
- [Handle DynamoDB provisioning exceptions cleaner (#29)](https://github.com/sebdah/dynamic-dynamodb/issues/29)

**0.4.1 (2013-04-10)**

- [No logging in --daemon mode (#21)](https://github.com/sebdah/dynamic-dynamodb/issues/21)

**0.4.0 (2013-04-06)**

- [Support for daemonizing Dynamic DynamoDB (#11)](https://github.com/sebdah/dynamic-dynamodb/issues/11)
- [Enhanced logging options (#4)](https://github.com/sebdah/dynamic-dynamodb/issues/4)
- [Add --version flag to dynamic-dynamodb command (#18)](https://github.com/sebdah/dynamic-dynamodb/issues/18)

**0.3.5 (2013-04-05)**

- [Handle missing table exceptions (#12)](https://github.com/sebdah/dynamic-dynamodb/issues/12)
- Bug fix: [No upscaling happening when scaling limit is exceeded (#16)](https://github.com/sebdah/dynamic-dynamodb/issues/16)

**0.3.4 (2013-04-05)**

- Bug fix: [Min/max limits seems to be read improperly from configuration files (#15)](https://github.com/sebdah/dynamic-dynamodb/issues/15)

**0.3.3 (2013-04-05)**

- Bug fix: [Mixup of read and writes provisioing in scaling (#14)](https://github.com/sebdah/dynamic-dynamodb/issues/14)

**0.3.2 (2013-04-05)**

- Bug fix: [Improper scaling under certain circumstances (#13)](https://github.com/sebdah/dynamic-dynamodb/issues/13)

**0.3.1 (2013-04-04)**

- Bug fix: [ValueError: Unknown format code 'd' for object of type 'str' (#10)](https://github.com/sebdah/dynamic-dynamodb/issues/10)

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

This project is maintained by [Sebastian Dahlgren](http://www.sebastiandahlgren.se) ([GitHub](https://github.com/sebdah) | [Twitter](https://twitter.com/sebdah) | [LinkedIn](http://www.linkedin.com/in/sebastiandahlgren))

License
-------

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
