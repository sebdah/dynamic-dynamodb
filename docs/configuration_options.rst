Configuration options
=====================

The sections below describe the various options available in the Dynamic DynamoDB configuration file. See :ref:`_example_configuration` for an example configuration file.

Global configuration
--------------------

**Section name:** ``[global]``

===================================== ========= ============= ==========================================
Option                                Type      Default       Comment
===================================== ========= ============= ==========================================
aws-access-key-id                     ``str``                 AWS access API key
aws-secret-access-key-id              ``str``                 AWS secret API key
check-interval                        ``int``   300           How many seconds to wait between the checks
circuit-breaker-timeout               ``float`` 10000.00      Timeout for the circuit breaker, in ms
circuit-breaker-url                   ``str``                 URL to poll for circuit breaking. Dynamic DynamoDB will only run if the circuit breaker returns ``HTTP/200``. When polling the URL, the headers ``x-table-name`` and ``x-gsi-name`` will be sent identifying the table and GSI names, if applicable.
region                                ``str``   ``us-east-1`` AWS region to use
===================================== ========= ============= ==========================================

Logging configuration
---------------------

**Section name:** ``[logging]``

===================================== ======= ============= ==========================================
Option                                Type    Default       Comment
===================================== ======= ============= ==========================================
log-file                              ``str``                Path to log file. Logging to stdout if this option is not present
log-level                             ``str``  ``info``      Log level (``debug``, ``info``, ``warning`` or ``error``)
log-config-file                       ``str``                Path to external Python logging configuration file. Overrides both ``log-level`` and ``log-file``. An example can be found in the Example configuration section.
===================================== ======= ============= ==========================================

Dynamic DynamoDB will rotate the ``log-file`` nightly per default and keep 5 days of backups. If you want to override this behavior, please have a look at the ``log-config-file`` option which allows you to use custom Python logging configuration files.

Table configuration
-------------------

**Section name:** ``[table: ^my_table$]``

Important note: The table name is treated as a regular expression. That means that ``my_table`` also will match ``my_table2``, unless you express it as a valid regular expression; ``^my_table$``. This feature enables you to easily configure many tables or tables with dynamic names.

=============================================== ========= =========================== ==========================================
Option                                          Type      Default                     Comment
=============================================== ========= =========================== ==========================================
allow-scaling-down-reads-on-0-percent           ``bool``  ``false``                   Allow down-scaling of reads when 0% is used.
allow-scaling-down-writes-on-0-percent          ``bool``  ``false``                   Allow down-scaling of writes when 0% is used.
always-decrease-rw-together                     ``bool``  ``false``                   Restrict scale down to only happen when both reads AND writes are in need of scaling down. Set this to ``true`` to minimize down-scaling.
circuit-breaker-timeout                         ``float`` 10000.00                    Timeout for the circuit breaker, in ms. Overrides the global setting if set.
circuit-breaker-url                             ``str``                               URL to poll for circuit breaking. Dynamic DynamoDB will only run if the circuit breaker returns ``HTTP/200``. Overrides the global setting if set. When polling the URL, the header ``x-table-name`` will be sent identifying the table name.
decrease-reads-unit                             ``str``   ``percent``                 Set if we should scale down reads in ``units`` or ``percent``
decrease-reads-with                             ``int``   50                          Number of ``units`` or ``percent`` we should scale down the read provisioning with. Choose entity with ``decrease-reads-unit``.
decrease-writes-unit                            ``str``   ``percent``                 Set if we should scale down in ``units`` or ``percent``
decrease-writes-with                            ``int``   50                          Number of ``units`` or ``percent`` we should scale down the write provisioning with. Choose entity with ``decrease-writes-unit``.
enable-reads-autoscaling                        ``bool``  ``true``                    Turn on or off autoscaling of read capacity. Deprecated! Please use ``enable-reads-up-scaling`` and ``enable-reads-down-scaling``
enable-reads-down-scaling                       ``bool``  ``true``                    Turn on or off of down scaling of read capacity
enable-reads-up-scaling                         ``bool``  ``true``                    Turn on or off of up scaling of read capacity
enable-writes-autoscaling                       ``bool``  ``true``                    Turn on or off autoscaling of write capacity. Deprecated! Please use ``enable-writes-up-scaling`` and ``enable-writes-down-scaling``
enable-writes-down-scaling                      ``bool``  ``true``                    Turn on or off of down scaling of write capacity
enable-writes-up-scaling                        ``bool``  ``true``                    Turn on or off of up scaling of write capacity
increase-consumed-reads-unit                    ``str``   ``increase-reads-unit``     Set if we should scale up reads based on the consumed metric in ``units`` or ``percent``
increase-consumed-reads-with                    ``int``   ``increase-reads-with``     Number of ``units`` or ``percent`` we should scale up read provisioning based on the consumed metric
increase-consumed-reads-scale                   ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up read provisioning based on the consumption metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.

                                                                                      If this is specified it will override ``increase-consumed-reads-with``
increase-consumed-writes-unit                   ``str``   ``increase-writes-unit``    Set if we should scale up writes based on the consumed metric in ``units`` or ``percent``
increase-consumed-writes-with                   ``int``   ``increase-writes-with``    Number of ``units`` or ``percent`` we should scale up write provisioning based on the consumed metric
increase-consumed-writes-scale                  ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up write provisioning based on the consumption metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.

                                                                                      If this is specified it will override ``increase-consumed-reads-with``
increase-reads-unit                             ``str``   ``percent``                 Set if we should scale up reads in ``units`` or ``percent``
increase-reads-with                             ``int``   50                          Number of ``units`` or ``percent`` we should scale up the read provisioning with. Choose entity with ``increase-reads-unit``.
increase-throttled-by-consumed-reads-unit       ``str``   ``increase-reads-unit``     Set if we should scale up reads based on throttled events with respect to consumption in ``units`` or ``percent``
increase-throttled-by-consumed-reads-scale      ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up read provisioning based on the throttled events with respect to consumption metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.
increase-throttled-by-consumed-writes-unit      ``str``   ``increase-writes-unit``    Set if we should scale up writes based on throttled events with respect to consumption in ``units`` or ``percent``
increase-throttled-by-consumed-writes-scale     ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up write provisioning based on the throttled events with respect to consumption metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.
increase-throttled-by-provisioned-reads-unit    ``str``   ``increase-reads-unit``     Set if we should scale up reads based on throttled events with respect to provisioning in ``units`` or ``percent``
increase-throttled-by-provisioned-reads-scale   ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up read provisioning based on the throttled events with respect to provisioning metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.
increase-throttled-by-provisioned-writes-unit   ``str``   ``increase-writes-unit``    Set if we should scale up writes based on throttled events with respect to provisioning in ``units`` or ``percent``
increase-throttled-by-provisioned-writes-scale  ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up write provisioning based on the throttled events with respect to provisioning metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.
increase-writes-unit                            ``str``   ``percent``                 Set if we should scale up in ``units`` or ``percent``
increase-writes-with                            ``int``   50                          Number of ``units`` or ``percent`` we should scale up the write provisioning with. Choose entity with ``increase-writes-unit``.
lookback-window-start                           ``int``   15                          Dynamic DynamoDB fetches data from CloudWatch in a window that streches between ``now()-15`` and ``now()-10`` minutes. If you want to look at slightly newer data, change this value. Please note that it might not be set to less than 1 minute (as CloudWatch data for DynamoDB is updated every minute).
lookback-period                                 ``int``   5                           Changes the duration of CloudWatch data to look at. For example, instead of looking at ``now()-15`` to ``now()-10``, you can look at ``now()-15`` to ``now()-14``
maintenance-windows                             ``str``                               Force Dynamic DynamoDB to operate within maintenance windows. E.g. ``22:00-23:59,00:00-06:00``
max-provisioned-reads                           ``int``                               Maximum number of provisioned reads for the table
max-provisioned-writes                          ``int``                               Maximum number of provisioned writes for the table
min-provisioned-reads                           ``int``                               Minimum number of provisioned reads for the table
min-provisioned-writes                          ``int``                               Minimum number of provisioned writes for the table
num-read-checks-before-scale-down               ``int``   1                           Force Dynamic DynamoDB to have `x` consecutive positive results before scaling reads down (`1` means scale down immediately)
num-read-checks-reset-percent                   ``int``   0                           Set a read consumption percentage when the `num-read-checks-before-scale-down` count should be reset. This option is optional, even if you use the `num-read-checks-before-scale-down` feature
num-write-checks-before-scale-down              ``int``   1                           Force Dynamic DynamoDB to have `x` consecutive positive results before scaling writes down (`1` means scale down immediately)
num-write-checks-reset-percent                  ``int``   0                           Set a write consumption percentage when the `num-write-checks-before-scale-down` count should be reset. This option is optional, even if you use the `num-write-checks-before-scale-down` feature
reads-lower-alarm-threshold                     ``int``                               How many percent of the reads capacity should be used before trigging the low throughput alarm?
reads-lower-threshold                           ``int``   30                          Scale down the reads with ``--decrease-reads-with`` if the currently consumed reads is as low as this percentage
reads-upper-alarm-threshold                     ``int``                               How many percent of the reads capacity should be used before trigging the high throughput alarm?
reads-upper-threshold                           ``float`` 90                          Scale up the reads with ``--increase-reads-with`` if the currently consumed reads reaches this many percent
sns-message-types                               ``str``                               Comma separated list of message types to receive SNS notifications for. Supported types are ``scale-up``, ``scale-down``, ``high-throughput-alarm`` and ``low-throughput-alarm``
sns-topic-arn                                   ``str``                               Full Topic ARN to use for sending SNS notifications
throttled-reads-upper-threshold                 ``int``   0                           Scale up the reads with ``--increase-reads-with`` if the count of throttled read events exceeds this count. Set to ``0`` (default) to turn off scaling based on throttled reads.

throttled-writes-upper-threshold                ``int``   0                           Scale up the writes with ``--increase-writes-with`` if the count of throttled write events exceeds this count. Set to ``0`` (default) to turn off scaling based on throttled reads.

writes-lower-alarm-threshold                    ``int``                               How many percent of the writes capacity should be used before trigging the low throughput alarm?
writes-lower-threshold                          ``int``   30                          Scale down the writes with ``--decrease-writes-with`` if the currently consumed writes is as low as this many percent
writes-upper-alarm-threshold                    ``int``                               How many percent of the writes capacity should be used before trigging the high throughput alarm?
writes-upper-threshold                          ``float`` 90                          Scale up the writes with ``--increase-writes-with`` if the currently consumed writes reaches this many percent
=============================================== ========= =========================== ==========================================


Global secondary index configuration
------------------------------------

**Section name:** ``[gsi: ^my_gsi$ table: ^my_table$]``

Important note: Both the GSI name and the table name is treated as regular expressions. That means that ``my_gsi`` also will match ``my_gsi``, unless you express it as a valid regular expression; ``^my_gsi$``. This feature enables you to easily configure many GSIs with one configuration section.

The ``table:`` section after ``gsi:`` **must** match with an existing ``table:`` section.

=============================================== ========= =========================== ==========================================
Option                                          Type      Default                     Comment
=============================================== ========= =========================== ==========================================
allow-scaling-down-reads-on-0-percent           ``bool``  ``false``                   Allow down-scaling of reads when 0% is used.
allow-scaling-down-writes-on-0-percent          ``bool``  ``false``                   Allow down-scaling of writes when 0% is used.
always-decrease-rw-together                     ``bool``  ``false``                   Restrict scale down to only happen when both reads AND writes are in need of scaling down. Set this to ``true`` to minimize down-scaling.
circuit-breaker-timeout                         ``float`` 10000.00                    Timeout for the circuit breaker, in ms. Overrides the global setting if set.
circuit-breaker-url                             ``str``                               URL to poll for circuit breaking. Dynamic DynamoDB will only run if the circuit breaker returns ``HTTP/200``. Overrides the global setting if set. When polling the URL, the headers ``x-table-name`` and ``x-gsi-name`` will be sent identifying the table and GSI names.
decrease-reads-unit                             ``str``   ``percent``                 Set if we should scale down reads in ``units`` or ``percent``
decrease-reads-with                             ``int``   50                          Number of ``units`` or ``percent`` we should scale down the read provisioning with. Choose entity with ``decrease-reads-unit``.
decrease-writes-unit                            ``str``   ``percent``                 Set if we should scale down in ``units`` or ``percent``
decrease-writes-with                            ``int``   50                          Number of ``units`` or ``percent`` we should scale down the write provisioning with. Choose entity with ``decrease-writes-unit``.
enable-reads-autoscaling                        ``bool``  ``true``                    Turn on or off autoscaling of read capacity. Deprecated! Please use ``enable-reads-up-scaling`` and ``enable-reads-down-scaling``
enable-reads-down-scaling                       ``bool``  ``true``                    Turn on or off of down scaling of read capacity
enable-reads-up-scaling                         ``bool``  ``true``                    Turn on or off of up scaling of read capacity
enable-writes-autoscaling                       ``bool``  ``true``                    Turn on or off autoscaling of write capacity. Deprecated! Please use ``enable-writes-up-scaling`` and ``enable-writes-down-scaling``
enable-writes-down-scaling                      ``bool``  ``true``                    Turn on or off of down scaling of write capacity
enable-writes-up-scaling                        ``bool``  ``true``                    Turn on or off of up scaling of write capacity
increase-consumed-reads-unit                    ``str``   ``increase-reads-unit``     Set if we should scale up reads based on the consumed metric in ``units`` or ``percent``
increase-consumed-reads-with                    ``int``   ``increase-reads-with``     Number of ``units`` or ``percent`` we should scale up read provisioning based on the consumed metric
increase-consumed-reads-scale                   ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up read provisioning based on the consumption metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.

                                                                                      If this is specified it will override ``increase-consumed-reads-with``
increase-consumed-writes-unit                   ``str``   ``increase-writes-unit``    Set if we should scale up writes based on the consumed metric in ``units`` or ``percent``
increase-consumed-writes-with                   ``int``   ``increase-writes-with``    Number of ``units`` or ``percent`` we should scale up write provisioning based on the consumed metric
increase-consumed-writes-scale                  ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up write provisioning based on the consumption metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.

                                                                                      If this is specified it will override ``increase-consumed-writes-with``
increase-reads-unit                             ``str``   ``percent``                 Set if we should scale up reads in ``units`` or ``percent``
increase-reads-with                             ``int``   50                          Number of ``units`` or ``percent`` we should scale up the read provisioning with. Choose entity with ``increase-reads-unit``.
increase-throttled-by-consumed-reads-unit       ``str``   ``increase-reads-unit``     Set if we should scale up reads based on throttled events with respect to consumption in ``units`` or ``percent``
increase-throttled-by-consumed-reads-scale      ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up read provisioning based on the throttled events with respect to consumption metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.
increase-throttled-by-consumed-writes-unit      ``str``   ``increase-writes-unit``    Set if we should scale up writes based on throttled events with respect to consumption in ``units`` or ``percent``
increase-throttled-by-consumed-writes-scale     ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up write provisioning based on the throttled events with respect to consumption metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.
increase-throttled-by-provisioned-reads-unit    ``str``   ``increase-reads-unit``     Set if we should scale up reads based on throttled events with respect to provisioning in ``units`` or ``percent``
increase-throttled-by-provisioned-reads-scale   ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up read provisioning based on the throttled events with respect to provisioning metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.
increase-throttled-by-provisioned-writes-unit   ``str``   ``increase-writes-unit``    Set if we should scale up writes based on throttled events with respect to provisioning in ``units`` or ``percent``
increase-throttled-by-provisioned-writes-scale  ``dict``                              Dictionary containing threshold/increment key/value pairs. We should use this to scale up write provisioning based on the throttled events with respect to provisioning metric.

                                                                                      Detailed information on the scale dict can be found `here <http://dynamic-dynamodb.readthedocs.org/en/latest/granular_scaling.html>`__.
increase-writes-unit                            ``str``   ``percent``                 Set if we should scale up in ``units`` or ``percent``
increase-writes-with                            ``int``   50                          Number of ``units`` or ``percent`` we should scale up the write provisioning with. Choose entity with ``increase-writes-unit``.
maintenance-windows                             ``str``                               Force Dynamic DynamoDB to operate within maintenance windows. E.g. ``22:00-23:59,00:00-06:00``
max-provisioned-reads                           ``int``                               Maximum number of provisioned reads for the table
max-provisioned-writes                          ``int``                               Maximum number of provisioned writes for the table
min-provisioned-reads                           ``int``                               Minimum number of provisioned reads for the table
min-provisioned-writes                          ``int``                               Minimum number of provisioned writes for the table
num-read-checks-before-scale-down               ``int``   1                           Force Dynamic DynamoDB to have `x` consecutive positive results before scaling reads down (`1` means scale down immediately)
num-read-checks-reset-percent                   ``int``   0                           Set a read consumption percentage when the `num-read-checks-before-scale-down` count should be reset. This option is optional, even if you use the `num-read-checks-before-scale-down` feature
num-write-checks-before-scale-down              ``int``   1                           Force Dynamic DynamoDB to have `x` consecutive positive results before scaling writes down (`1` means scale down immediately)
num-write-checks-reset-percent                  ``int``   0                           Set a write consumption percentage when the `num-write-checks-before-scale-down` count should be reset. This option is optional, even if you use the `num-write-checks-before-scale-down` feature
reads-lower-alarm-threshold                     ``int``                               How many percent of the reads capacity should be used before trigging the low throughput alarm?
reads-lower-threshold                           ``int``   30                          Scale down the reads with ``--decrease-reads-with`` if the currently consumed reads is as low as this percentage
reads-upper-alarm-threshold                     ``int``                               How many percent of the reads capacity should be used before trigging the high throughput alarm?
reads-upper-threshold                           ``float`` 90                          Scale up the reads with ``--increase-reads-with`` if the currently consumed reads reaches this many percent
sns-message-types                               ``str``                               Comma separated list of message types to receive SNS notifications for. Supported types are ``scale-up`` , ``scale-down``, ``high-throughput-alarm`` and ``low-throughput-alarm``
sns-topic-arn                                   ``str``                               Full Topic ARN to use for sending SNS notifications
throttled-reads-upper-threshold                 ``int``   0                           Scale up the reads with ``--increase-reads-with`` if the count of throttled read events exceeds this count. Set to ``0`` (default) to turn off scaling based on throttled reads.

throttled-writes-upper-threshold                ``int``   0                           Scale up the writes with ``--increase-writes-with`` if the count of throttled write events exceeds this count. Set to ``0`` (default) to turn off scaling based on throttled reads.

writes-lower-alarm-threshold                    ``int``                               How many percent of the writes capacity should be used before trigging the low throughput alarm?
writes-lower-threshold                          ``int``   30                          Scale down the writes with ``--decrease-writes-with`` if the currently consumed writes is as low as this many percent
writes-upper-alarm-threshold                    ``int``                               How many percent of the writes capacity should be used before trigging the high throughput alarm?
writes-upper-threshold                          ``float`` 90                          Scale up the writes with ``--increase-writes-with`` if the currently consumed writes reaches this many percent
=============================================== ========= =========================== ==========================================

Default configuration
---------------------

**Section name:** ``[default_options]``

Are you tired of setting the same configuration options for multiple tables or indexes? Then use the ``[default_options]`` section. It will let you create default values for all your tables and indexes. You can of course override those values by setting other values in your table or index specific configuration.

