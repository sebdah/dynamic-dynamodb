Dynamic DynamoDB configuration
==============================

The sections below describe the various options available in the Dynamic DynamoDB configuration file. See :ref:`_example_configuration_file`.

Global options
--------------

**Section name:** ``[global]``

===================================== ==== ==========================================
Option                                Type Comment
===================================== ==== ==========================================
``aws-access-key-id``                 str  AWS access API key
``aws-secret-access-key-id``          str  AWS secret API key
``region``                            str  AWS region to use. E.g. ``us-east-1``
``check-interval``                    int  How many seconds to wait between the checks. Important if running in daemon mode.
``circuit-breaker-url``               str  URL to poll for circuit breaking. Dynamic DynamoDB will only run if the circuit breaker returns ``HTTP/200``
``circuit-breaker-timeout``           int  Timeout for the circuit breaker, in ms
===================================== ==== ==========================================
