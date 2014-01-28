Release notes
=============

1.7.3
-----

**Release date:** 2014-01-28

-  `circuit breaker option bailing out w/ exception #105 <https://github.com/sebdah/dynamic-dynamodb/issues/105>`__

1.7.2
-----

**Release date:** 2014-01-23

-  `CU increases fail if decreases fail due to exceeded limits #103 <https://github.com/sebdah/dynamic-dynamodb/issues/103>`__

1.7.1
-----

**Release date:** 2014-01-04

-  `Rounding increase values up #100 <https://github.com/sebdah/dynamic-dynamodb/issues/100>`__
-  `Fixed bug with configuration for multiple tables #101 <https://github.com/sebdah/dynamic-dynamodb/issues/100>`__. Thanks `@msh9 <https://github.com/msh9>`__!

1.7.0
-----

**Release date:** 2013-12-26

-  `Added support for global secondary indexes #73 <https://github.com/sebdah/dynamic-dynamodb/issues/73>`__
-  Fixed `Log level configuration in configuration file is overridden #75 <https://github.com/sebdah/dynamic-dynamodb/issues/75>`__
-  `Recursively retrieve all tables #84 <https://github.com/sebdah/dynamic-dynamodb/issues/84>`__. Submitted by `@alxmrtn <https://github.com/alxmrtn>`__
-  `Loop dynamic-dynamodb in command line mode #91 <https://github.com/sebdah/dynamic-dynamodb/issues/91>`__
-  `Migrated to ``boto.dynamodb2`` #72 <https://github.com/sebdah/dynamic-dynamodb/issues/72>`__
-  `Describe configuration options in the documentation #80 <https://github.com/sebdah/dynamic-dynamodb/issues/80>`__
-  `Move release notes to the documentation #79 <https://github.com/sebdah/dynamic-dynamodb/issues/79>`__
- Better exception handling fixed in `#96 <https://github.com/sebdah/dynamic-dynamodb/issues/96>`__, `#97 <https://github.com/sebdah/dynamic-dynamodb/issues/97>`__ and `#98 <https://github.com/sebdah/dynamic-dynamodb/issues/98>`__
-  `Silently skipping configured tables that does not exist in DynamoDB #94 <https://github.com/sebdah/dynamic-dynamodb/issues/94>`__
- Enhanced `configuration validation #93 <https://github.com/sebdah/dynamic-dynamodb/issues/93>`__

A full list of closed issues can be found `here <https://github.com/sebdah/dynamic-dynamodb/issues?milestone=29&page=1&state=closed>`__

Special thanks to the AWS DynamoDB for their support with this release.

1.6.0
-----

**Release date:** 2013-11-21

-  Documented project in Sphinx -
   http://dynamic-dynamodb.readthedocs.org
-  Fixed `Failure on non-matching regular expressions
   #69 <https://github.com/sebdah/dynamic-dynamodb/issues/69>`__
-  Fixed bug `cleanup logs in case of noop updates
   #71 <https://github.com/sebdah/dynamic-dynamodb/issues/71>`__ -
   Thanks [@tmorgan](https://github.com/tmorgan)

1.5.8
-----

**Release date:** 2013-10-18

-  Fixed bug `Under some circumstances Dynamic DynamoDB crashes when
   table is deleted
   #68 <https://github.com/sebdah/dynamic-dynamodb/issues/68>`__

1.5.7
-----

**Release date:** 2013-10-17

-  Closed `Support for running dynamic-dynamodb with supervisord
   #66 <https://github.com/sebdah/dynamic-dynamodb/issues/66>`__ with
   `Pull Request
   #67 <https://github.com/sebdah/dynamic-dynamodb/pull/67>`__. Thanks
   @pragnesh!

1.5.6
-----

**Release date:** 2013-10-06

-  `Fixed issue where DDB didn't support increasing capacity two times
   #65 <https://github.com/sebdah/dynamic-dynamodb/pull/65>`__

1.5.5
-----

**Release date:** 2013-08-31

-  `Change log level of informational
   message <https://github.com/sebdah/dynamic-dynamodb/issues/62>`__

1.5.4
-----

**Release date:** 2013-08-29

-  `Added missing ``key_name``
   parameter <https://github.com/sebdah/dynamic-dynamodb/issues/60>`__

1.5.3
-----

**Release date:** 2013-08-27

-  `Added missing sleep statement
   fixes <https://github.com/sebdah/dynamic-dynamodb/issues/58>`__

1.5.2
-----

**Release date:** 2013-08-27

-  `Issue with ``always-decrease-rw-together``
   option <https://github.com/sebdah/dynamic-dynamodb/issues/55>`__
-  `ListTables permission
   required <https://github.com/sebdah/dynamic-dynamodb/issues/57>`__

The AWS ``ListTables`` permission is no longer a hard requirement. It's
only needed if you're using regular expressions to configure your
DynamoDB tables.

1.5.1
-----

**Release date:** 2013-08-22

-  `No module named
   core <https://github.com/sebdah/dynamic-dynamodb/issues/53>`__ (fixed
   by `#54 <https://github.com/sebdah/dynamic-dynamodb/pull/54>`__)

Fixed bug in the 1.5.0 release.

1.5.0
-----

**Release date:** 2013-08-22

-  `Support for regular expressions in
   config <https://github.com/sebdah/dynamic-dynamodb/issues/52>`__

Thanks [@pragnesh](https://github.com/pragnesh) for adding this feature!

1.4.0
-----

**Release date:** 2013-08-14

-  `Retrying failed DynamoDB
   connections <https://github.com/sebdah/dynamic-dynamodb/issues/51>`__

1.3.6
-----

**Release date:** 2013-07-21

-  `int() argument must be a string or a number, not 'NoneType'
   (#50) <https://github.com/sebdah/dynamic-dynamodb/issues/50>`__

1.3.5
-----

**Release date:** 2013-06-17

-  `increase\_writes\_unit parameter is used while it should be
   decrease\_writes\_unit
   (#47) <https://github.com/sebdah/dynamic-dynamodb/issues/47>`__

1.3.4
-----

**Release date:** 2013-06-13

-  `An attempt to update provisioning is made even if the requested
   values are equal to the tables current values
   (#46) <https://github.com/sebdah/dynamic-dynamodb/issues/46>`__

1.3.3
-----

**Release date:** 2013-06-08

-  `Increasing to a minimum provisioned throughput value doesn't take
   into account the current table's throughput
   (#45) <https://github.com/sebdah/dynamic-dynamodb/issues/45>`__
-  `dynamic-dynamodb --version causes AttributeError in cli
   (#44) <https://github.com/sebdah/dynamic-dynamodb/issues/44>`__

1.3.2
-----

**Release date:** 2013-05-14

-  `increase\_reads\_in\_percent calculations are incorrect
   (#40) <https://github.com/sebdah/dynamic-dynamodb/issues/40>`__

1.3.1
-----

**Release date:** 2013-05-10

-  `Fix Python 2.6 support
   (#39) <https://github.com/sebdah/dynamic-dynamodb/issues/39>`__

1.3.0
-----

**Release date:** 2013-05-01

This Dynamic DynamoDB release makes it possible to use multiple Dynamic
DynamoDB instances in parallel in daemon mode. Simply use the
``--instance`` flag to separate the difference instances with a unique
name. Then control them as usual with the ``--daemon`` flag.

-  `Allow to run multiple instances in parallel
   (#37) <https://github.com/sebdah/dynamic-dynamodb/issues/37>`__

1.2.5
-----

**Release date:** 2013-04-29

-  `Handle ResourceInUseException better
   (#36) <https://github.com/sebdah/dynamic-dynamodb/issues/36>`__
-  `Add --log-level option to command line
   (#34) <https://github.com/sebdah/dynamic-dynamodb/issues/34>`__

1.2.4
-----

**Release date:** 2013-04-26

-  `Mix up between percent and units
   (#35) <https://github.com/sebdah/dynamic-dynamodb/issues/35>`__
-  Broken build fixed

1.2.0
-----

**Release date:** 2013-04-20

-  `Add support for dead-man's-switch API call
   (#25) <https://github.com/sebdah/dynamic-dynamodb/issues/25>`__

1.1.0
-----

**Release date:** 2013-04-17

-  `Update provisioning in units not just percentage
   (#22) <https://github.com/sebdah/dynamic-dynamodb/issues/22>`__
-  `Increase in percent does not add to current provisioning properly
   (#33) <https://github.com/sebdah/dynamic-dynamodb/issues/33>`__
-  `Enhance configuration option validation
   (#32) <https://github.com/sebdah/dynamic-dynamodb/issues/32>`__

1.0.1
-----

**Release date:** 2013-04-17

-  Minor fix: Ugly output removed

1.0.0
-----

**Release date:** 2013-04-16

The 1.0.0 release is a leap forward when it comes to module structure
and extendability. Please remember that this is still Release in beta in
PyPI, so all bug reports are very welcome. File any odd behavior or bugs
in `GitHub
Issues <https://github.com/sebdah/dynamic-dynamodb/issues>`__.

-  `Restructure the Dynamic DynamoDB code base
   (#30) <https://github.com/sebdah/dynamic-dynamodb/issues/30>`__
-  `Support multiple tables in one configuration file
   (#19) <https://github.com/sebdah/dynamic-dynamodb/issues/19>`__
-  `Change pid file name
   (#31) <https://github.com/sebdah/dynamic-dynamodb/issues/31>`__
-  `Handle combinations of configuration file and command line options
   better
   (#24) <https://github.com/sebdah/dynamic-dynamodb/issues/24>`__

0.5.0
-----

**Release date:** 2013-04-12

-  `Add --log-file command line option
   (#20) <https://github.com/sebdah/dynamic-dynamodb/issues/20>`__
-  `Allow scale down at 0% consumed count
   (#17) <https://github.com/sebdah/dynamic-dynamodb/issues/17>`__
-  `"only downscale reads AND writes" option would be useful
   (#23) <https://github.com/sebdah/dynamic-dynamodb/issues/23>`__

0.4.2
-----

**Release date:** 2013-04-11

-  `Unhandled exception: ValidationException
   (#28) <https://github.com/sebdah/dynamic-dynamodb/issues/28>`__
-  `Handle DynamoDB provisioning exceptions cleaner
   (#29) <https://github.com/sebdah/dynamic-dynamodb/issues/29>`__

0.4.1
-----

**Release date:** 2013-04-10

-  `No logging in --daemon mode
   (#21) <https://github.com/sebdah/dynamic-dynamodb/issues/21>`__

0.4.0
-----

**Release date:** 2013-04-06

-  `Support for daemonizing Dynamic DynamoDB
   (#11) <https://github.com/sebdah/dynamic-dynamodb/issues/11>`__
-  `Enhanced logging options
   (#4) <https://github.com/sebdah/dynamic-dynamodb/issues/4>`__
-  `Add --version flag to dynamic-dynamodb command
   (#18) <https://github.com/sebdah/dynamic-dynamodb/issues/18>`__

0.3.5
-----

**Release date:** 2013-04-05

-  `Handle missing table exceptions
   (#12) <https://github.com/sebdah/dynamic-dynamodb/issues/12>`__
-  Bug fix: `No upscaling happening when scaling limit is exceeded
   (#16) <https://github.com/sebdah/dynamic-dynamodb/issues/16>`__

0.3.4
-----

**Release date:** 2013-04-05

-  Bug fix: `Min/max limits seems to be read improperly from
   configuration files
   (#15) <https://github.com/sebdah/dynamic-dynamodb/issues/15>`__

0.3.3
-----

**Release date:** 2013-04-05

-  Bug fix: `Mixup of read and writes provisioing in scaling
   (#14) <https://github.com/sebdah/dynamic-dynamodb/issues/14>`__

0.3.2
-----

**Release date:** 2013-04-05

-  Bug fix: `Improper scaling under certain circumstances
   (#13) <https://github.com/sebdah/dynamic-dynamodb/issues/13>`__

0.3.1
-----

**Release date:** 2013-04-04

-  Bug fix: `ValueError: Unknown format code 'd' for object of type
   'str' (#10) <https://github.com/sebdah/dynamic-dynamodb/issues/10>`__

0.3.0
-----

**Release date:** 2013-03-27

This release contains support for configuration files, custom AWS access
keys and configurable maintenance windows. The maintenance feature will
restrict Dynamic DynamoDB to change your provisioning only during
specific time slots.

-  `Add support for configuration files
   (#6) <https://github.com/sebdah/dynamic-dynamodb/issues/6>`__
-  `Configure AWS credentials on command line
   (#5) <https://github.com/sebdah/dynamic-dynamodb/issues/5>`__
-  `Support for maintenance windows
   (#1) <https://github.com/sebdah/dynamic-dynamodb/issues/1>`__

0.2.0
-----

**Release date:** 2013-03-24 - First public release

0.1.1
-----

**Release date:** 2013-03-24 - Initial release
