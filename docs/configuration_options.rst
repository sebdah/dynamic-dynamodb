Configuration options
=====================

The sections below describe the various options available in the Dynamic DynamoDB configuration file. See :ref:`_example_configuration <Example configuration>` for an example configuration file.

Global configuration
--------------------

**Section name:** ``[global]``

===================================== ==== ==========================================
Option                                Type Comment
===================================== ==== ==========================================
aws-access-key-id                     str  AWS access API key
aws-secret-access-key-id              str  AWS secret API key
region                                str  AWS region to use. E.g. ``us-east-1``
check-interval                        int  How many seconds to wait between the checks. Default is 300 seconds.
circuit-breaker-url                   str  URL to poll for circuit breaking. Dynamic DynamoDB will only run if the circuit breaker returns ``HTTP/200``
circuit-breaker-timeout               int  Timeout for the circuit breaker, in ms
===================================== ==== ==========================================

Logging configuration
---------------------

**Section name:** ``[logging]``

===================================== ==== ==========================================
Option                                Type Comment
===================================== ==== ==========================================
log-level                             str  Log level (``debug``, ``info``, ``warning`` or ``error``)
log-file                              str  Path to log file. Logging to stdout if this option is not present
log-config-file                       str  Path to external Python logging configuration file. Overrides both ``log-level`` and ``log-file``. An example can be found in the Example configuration section.
===================================== ==== ==========================================

Dynamic DynamoDB will rotate the ``log-file`` nightly per default and keep 5 days of backups. If you want to override this behavior, please have a look at the ``log-config-file`` option which allows you to use custom Python logging configuration files.

Table configuration
-------------------

**Section name:** ``[table: ^my_table$]``

Important note: The table name is treated as a regular expression. That means that ``my_table`` also will match ``my_table2``, unless you express it as a valid regular expression; ``^my_table$``. This feature enables you to easily configure many tables or tables with dynamic names.

========================================== ==== ==========================================
Option                                     Type Comment
========================================== ==== ==========================================
enable-reads-autoscaling                   bool Turn on or off autoscaling of read capacity. Default is ``true``
enable-writes-autoscaling                  bool Turn on or off autoscaling of write capacity. Default is ``true``
reads-upper-threshold                      int  Scale up the reads with ``--increase-reads-with`` if the currently consumed reads reaches this many percent
reads-lower-threshold                      int  Scale down the reads with ``--decrease-reads-with`` if the currently consumed reads is as low as this percentage
throttled-reads-upper-threshold            int  Scale up the reads with ``--increase-reads-with`` if the count of throttled read events exceeds this count
increase-reads-with                        int  Number of ``units`` or ``percent`` we should scale up the read provisioning with. Choose entity with ``increase-reads-unit``.
decrease-reads-with                        int  Number of ``units`` or ``percent`` we should scale down the read provisioning with. Choose entity with ``decrease-reads-unit``.
increase-reads-unit                        str  Set if we should scale up reads in ``units`` or ``percent``
decrease-reads-unit                        str  Set if we should scale down reads in ``units`` or ``percent``
min-provisioned-reads                      int  Minimum number of provisioned reads for the table
max-provisioned-reads                      int  Maximum number of provisioned reads for the table
writes-upper-threshold                     int  Scale up the writes with ``--increase-writes-with`` if the currently consumed writes reaches this many percent
writes-lower-threshold                     int  Scale down the writes with ``--decrease-writes-with`` if the currently consumed writes is as low as this many percent
throttled-writes-upper-threshold           int  Scale up the writes with ``--increase-writes-with`` if the count of throttled write events exceeds this count
increase-writes-with                       int  Number of ``units`` or ``percent`` we should scale up the write provisioning with. Choose entity with ``increase-writes-unit``.
decrease-writes-with                       int  Number of ``units`` or ``percent`` we should scale down the write provisioning with. Choose entity with ``decrease-writes-unit``.
increase-writes-unit                       str  Set if we should scale up in ``units`` or ``percent``
decrease-writes-unit                       str  Set if we should scale down in ``units`` or ``percent``
min-provisioned-writes                     int  Minimum number of provisioned writes for the table
max-provisioned-writes                     int  Maximum number of provisioned writes for the table
num-read-checks-before-scale-down          int  Force Dynamic DynamoDB to have `x` consecutive positive results before scaling down. Default is `1` (i.e. scale down immediately)
num-write-checks-before-scale-down         int  Force Dynamic DynamoDB to have `x` consecutive positive results before scaling down. Default is `1` (i.e. scale down immediately)
num-read-checks-reset-percent              int  Set a read consumption percentage when the `num-read-checks-before-scale-down` count should be reset. This option is optional, even if you use the `num-read-checks-before-scale-down` feature
num-write-checks-reset-percent             int  Set a write consumption percentage when the `num-write-checks-before-scale-down` count should be reset. This option is optional, even if you use the `num-write-checks-before-scale-down` feature
maintenance-windows                        str  Force Dynamic DynamoDB to operate within maintenance windows. E.g. ``22:00-23:59,00:00-06:00``
sns-topic-arn                              str  Full Topic ARN to use for sending SNS notifications
sns-message-types                          str  Comma separated list of message types to receive SNS notifications for. Supported types are ``scale-up`` and ``scale-down``
allow-scaling-down-reads-on-0-percent      bool Allow down scaling of read units when 0% is used.
allow-scaling-down-writes-on-0-percent     bool Allow down scaling of write units when 0% is used.
always-decrease-rw-together                bool Restrict scale down to only happen when both reads AND writes are in need of scaling down. Set this to ``true`` to minimize down scaling.
========================================== ==== ==========================================

Global secondary index configuration
------------------------------------

**Section name:** ``[gsi: ^my_gsi$ table: ^my_table$]``

Important note: Both the GSI name and the table name is treated as regular expressions. That means that ``my_gsi`` also will match ``my_gsi``, unless you express it as a valid regular expression; ``^my_gsi$``. This feature enables you to easily configure many GSIs with one configuration section.

The ``table:`` section after ``gsi:`` **must** match with an existing ``table:`` section.

========================================== ==== ==========================================
Option                                     Type Comment
========================================== ==== ==========================================
enable-reads-autoscaling                   bool Turn on or off autoscaling of read capacity. Default is ``true``
enable-writes-autoscaling                  bool Turn on or off autoscaling of write capacity. Default is ``true``
reads-upper-threshold                      int  Scale up the reads with ``--increase-reads-with`` if the currently consumed reads reaches this many percent
reads-lower-threshold                      int  Scale down the reads with ``--decrease-reads-with`` if the currently consumed reads is as low as this percentage
throttled-reads-upper-threshold            int  Scale up the reads with ``--increase-reads-with`` if the count of throttled read events exceeds this count
increase-reads-with                        int  Number of ``units`` or ``percent`` we should scale up the read provisioning with. Choose entity with ``increase-reads-unit``.
decrease-reads-with                        int  Number of ``units`` or ``percent`` we should scale down the read provisioning with. Choose entity with ``decrease-reads-unit``.
increase-reads-unit                        str  Set if we should scale up in ``units`` or ``percent``
decrease-reads-unit                        str  Set if we should scale down in ``units`` or ``percent``
min-provisioned-reads                      int  Minimum number of reads for the table
max-provisioned-reads                      int  Maximum number of reads for the table
writes-upper-threshold                     int  Scale up the writes with ``--increase-writes-with`` if the currently consumed writes reaches this many percent
writes-lower-threshold                     int  Scale down the writes with ``--decrease-writes-with`` if the currently consumed writes is as low as this many percent
throttled-writes-upper-threshold           int  Scale up the writes with ``--increase-writes-with`` if the count of throttled write events exceeds this count
increase-writes-with                       int  Number of ``units`` or ``percent`` we should scale up the write provisioning with. Choose entity with ``increase-writes-unit``.
decrease-writes-with                       int  Number of ``units`` or ``percent`` we should scale down the write provisioning with. Choose entity with ``decrease-writes-unit``.
increase-writes-unit                       str  Set if we should scale up in ``units`` or ``percent``
decrease-writes-unit                       str  Set if we should scale down in ``units`` or ``percent``
min-provisioned-writes                     int  Minimum number of writes for the table
max-provisioned-writes                     int  Maximum number of writes for the table
num-read-checks-before-scale-down          int  Force Dynamic DynamoDB to have `x` consecutive positive results before scaling down. Default is `1` (i.e. scale down immediately)
num-write-checks-before-scale-down         int  Force Dynamic DynamoDB to have `x` consecutive positive results before scaling down. Default is `1` (i.e. scale down immediately)
num-read-checks-reset-percent              int  Set a read consumption percentage when the `num-read-checks-before-scale-down` count should be reset. This option is optional, even if you use the `num-read-checks-before-scale-down` feature
num-write-checks-reset-percent             int  Set a write consumption percentage when the `num-write-checks-before-scale-down` count should be reset. This option is optional, even if you use the `num-write-checks-before-scale-down` feature
maintenance-windows                        str  Force Dynamic DynamoDB to operate within maintenance windows. E.g. ``22:00-23:59,00:00-06:00``
sns-topic-arn                              str  Full Topic ARN to use for sending SNS notifications
sns-message-types                          str  Comma separated list of message types to receive SNS notifications for. Supported types are ``scale-up`` and ``scale-down``
allow-scaling-down-reads-on-0-percent      bool Allow down scaling of read units when 0% is used.
allow-scaling-down-writes-on-0-percent     bool Allow down scaling of write units when 0% is used.
always-decrease-rw-together                bool Restrict scale down to only happen when both reads AND writes are in need of scaling down. Set this to ``true`` to minimize down scaling.
========================================== ==== ==========================================
