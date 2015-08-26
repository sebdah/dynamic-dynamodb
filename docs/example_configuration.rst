.. _example_configuration:

Example configuration files
===========================

Example ``dynamic-dynamodb.conf``
---------------------------------

This is a full example of a Dynamic DynamoDB configuration file.
::

    [global]
    # AWS access keys
    aws-access-key-id: AWS_ACCESS_KEY
    aws-secret-access-key-id: AWS_SECRET_KEY

    # AWS region to use
    region: us-east-1

    # How often should Dynamic DynamoDB monitor changes (in seconds)
    check-interval: 300

    # Circuit breaker configuration
    # No provisioning updates will be made unless this URL returns
    # a HTTP 200 OK status code
    #circuit-breaker-url: http://my.service.com/v1/is_up
    #circuit-breaker-timeout: 500

    [logging]
    # Log level [debug|info|warning|error]
    log-level: info

    # Log file (comment out to get only console output)
    log-file: /var/log/dynamic-dynamodb.log

    # External Python logging configuration file
    # Overrides both log-level and log-file
    # log-config-file: /path/to/logging.conf

    [table: ^my_table$]
    #
    # Read provisioning configuration
    #
    
    # Thresholds for trigging throughput alarm to send notification (%)
    # reads-upper-alarm-threshold: 0
    # reads-lower-alarm-threshold: 0

    # Enable or disable reads autoscaling
    enable-reads-autoscaling = true

    # Thresholds for scaling up or down the provisioning (%)
    reads-upper-threshold: 90
    reads-lower-threshold: 30

    # How many percent should Dynamic DynamoDB increase/decrease provisioning with (%)
    increase-reads-with: 50
    decrease-reads-with: 50

    # Units to increase or decrease reads with, must be either percent or units
    increase-reads-unit: percent
    decrease-reads-unit: percent

    # Maximum and minimum read provisioning
    # Dynamic DynamoDB will not provision any more or less reads than this
    min-provisioned-reads: 1
    max-provisioned-reads: 500

    #
    # Write provisioning configuration
    #

    # Threshold for trigging throughput alarm to send notification (%)
    # writes-upper-alarm-threshold: 0
    # writes-lower-alarm-threshold: 0

    # Enable or disable writes autoscaling
    enable-writes-autoscaling = true

    # Thresholds for scaling up or down the provisioning (%)
    writes-upper-threshold: 90
    writes-lower-threshold: 30

    # How many percent should Dynamic DynamoDB increase/decrease provisioning with (%)
    increase-writes-with: 50
    decrease-writes-with: 50

    # Units to increase or decrease writes with, must be either percent or units
    increase-writes-unit: percent
    decrease-writes-unit: percent

    # Maximum and minimum write provisioning
    # Dynamic DynamoDB will not provision any more or less writes than this
    min-provisioned-writes: 1
    max-provisioned-writes: 500

    #
    # Maintenance windows (in UTC)
    #
    #maintenance-windows: 22:00-23:59,00:00-06:00

    #
    # Simple Notification Service configuration
    #

    # Topic ARN to publish notifications to
    #
    # Example:
    # sns-topic-arn: arn:aws:sns:us-east-1:123456789012:dynamic-dynamodb-my_table

    # Message types to send as SNS notifications
    #
    # Comma separated list. Currently supported values:
    # - scale-up                    Get notifications when the table is scaled up
    # - scale-down                  Get notifications when the table is scaled down
    # - high-throughput-alarm       Get notifications when exceed high throughput threshold
    # - low-throughput-alarm        Get notifications when below low throughput threshold
    #
    # Example:
    # sns-message-types: scale-up, scale-down, high-throughput-alarm, low-throughput-alarm

    #
    # Other settings
    #

    # Allow down scaling when at 0% consumed reads
    #allow-scaling-down-reads-on-0-percent: true
    #allow-scaling-down-writes-on-0-percent: true

    # Restrict scale down to only happen when BOTH reads AND writes are in need
    # of scaling down. Set this to "true" to minimize down scaling.
    #always-decrease-rw-together: true

    [gsi: ^my_gsi$ table: ^my_table$]
    #
    # Read provisioning configuration
    #

    # Thresholds for trigging throughput alarm to send notification (%)
    # reads-upper-alarm-threshold: 0
    # reads-lower-alarm-threshold: 0

    # Enable or disable reads autoscaling
    enable-reads-autoscaling = true

    # Thresholds for scaling up or down the provisioning (%)
    reads-upper-threshold: 90
    reads-lower-threshold: 30

    # How many percent should Dynamic DynamoDB increase/decrease provisioning with (%)
    increase-reads-with: 50
    decrease-reads-with: 50

    # Units to increase or decrease reads with, must be either percent or units
    increase-reads-unit: percent
    decrease-reads-unit: percent

    # Maximum and minimum read provisioning
    # Dynamic DynamoDB will not provision any more or less reads than this
    min-provisioned-reads: 1
    max-provisioned-reads: 500

    #
    # Write provisioning configuration
    #

    # Threshold for trigging throughput alarm to send notification (%)
    # writes-upper-alarm-threshold: 0
    # writes-lower-alarm-threshold: 0

    # Enable or disable writes autoscaling
    enable-writes-autoscaling = true

    # Thresholds for scaling up or down the provisioning (%)
    writes-upper-threshold: 90
    writes-lower-threshold: 30

    # How many percent should Dynamic DynamoDB increase/decrease provisioning with (%)
    increase-writes-with: 50
    decrease-writes-with: 50

    # Units to increase or decrease writes with, must be either percent or units
    increase-writes-unit: percent
    decrease-writes-unit: percent

    # Maximum and minimum write provisioning
    # Dynamic DynamoDB will not provision any more or less writes than this
    min-provisioned-writes: 1
    max-provisioned-writes: 500

    #
    # Maintenance windows (in UTC)
    #
    #maintenance-windows: 22:00-23:59,00:00-06:00

    #
    # Simple Notification Service configuration
    #

    # Topic ARN to publish notifications to
    #
    # Example:
    # sns-topic-arn: arn:aws:sns:us-east-1:123456789012:dynamic-dynamodb-my_table

    # Message types to send as SNS notifications
    #
    # Comma separated list. Currently supported values:
    # - scale-up                    Get notifications when the table is scaled up
    # - scale-down                  Get notifications when the table is scaled 
    # - high-throughput-alarm       Get notifications when exceed high throughput threshold
    # - low-throughput-alarm        Get notifications when below low throughput threshold
    #
    # Example:
    # sns-message-types: scale-up, scale-down, high-throughput-alarm, low-throughput-alarm

    #
    # Other settings
    #

    # Allow down scaling when at 0% consumed reads
    #allow-scaling-down-reads-on-0-percent: true
    #allow-scaling-down-writes-on-0-percent: true

    # Restrict scale down to only happen when BOTH reads AND writes are in need
    # of scaling down. Set this to "true" to minimize down scaling.
    #always-decrease-rw-together: true

Note: The configuration of tables support regular expressions so you could write ``[table: log_.* ]`` if you want to target multiple tables with one config section, however if a table name matches the regex of more than one section, only the first match will be used.  (This will let you set a ``[table: .*]`` section at the end as a catchall.)


Example ``logging.conf``
------------------------

Below is an example of a logging configuration file used with the ``--log-config-file`` and ``log-config-file`` options. This kind of external logging configuration enables users to log through syslog, via custom log handlers or to other external services. It will also give control over logrotation and similar log management functions.
::

    [loggers]
    keys=root

    [logger_root]
    handlers=console,file
    level=NOTSET

    [formatters]
    keys=default

    [formatter_default]
    format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

    [handlers]
    keys=file,console

    [handler_file]
    class=handlers.TimedRotatingFileHandler
    interval=midnight
    backupCount=7
    formatter=default
    level=DEBUG
    args=('/Users/sebastian/dynamic-dynamodb2.log',)

    [handler_console]
    class=StreamHandler
    formatter=default
    level=INFO
    args=(sys.stdout,)
