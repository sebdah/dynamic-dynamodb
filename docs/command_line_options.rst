Command line options
====================

Below is a listing of Dynamic DynamoDB's command line parameters.
::

    usage: dynamic-dynamodb [-h] [-c CONFIG] [--dry-run]
                            [--check-interval CHECK_INTERVAL]
                            [--log-file LOG_FILE]
                            [--log-level {debug,info,warning,error}]
                            [--log-config-file LOG_CONFIG_FILE] [--version]
                            [--aws-access-key-id AWS_ACCESS_KEY_ID]
                            [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
                            [--daemon DAEMON] [--instance INSTANCE]
                            [--pid-file-dir PID_FILE_DIR] [-r REGION]
                            [-t TABLE_NAME]
                            [--reads-upper-threshold READS_UPPER_THRESHOLD]
                            [--throttled-reads-upper-threshold THROTTLED_READS_UPPER_THRESHOLD]
                            [--reads-lower-threshold READS_LOWER_THRESHOLD]
                            [--increase-reads-with INCREASE_READS_WITH]
                            [--decrease-reads-with DECREASE_READS_WITH]
                            [--increase-reads-unit INCREASE_READS_UNIT]
                            [--decrease-reads-unit DECREASE_READS_UNIT]
                            [--min-provisioned-reads MIN_PROVISIONED_READS]
                            [--max-provisioned-reads MAX_PROVISIONED_READS]
                            [--num-read-checks-before-scale-down NUM_READ_CHECKS_BEFORE_SCALE_DOWN]
                            [--writes-upper-threshold WRITES_UPPER_THRESHOLD]
                            [--throttled-writes-upper-threshold THROTTLED_WRITES_UPPER_THRESHOLD]
                            [--writes-lower-threshold WRITES_LOWER_THRESHOLD]
                            [--increase-writes-with INCREASE_WRITES_WITH]
                            [--decrease-writes-with DECREASE_WRITES_WITH]
                            [--increase-writes-unit INCREASE_WRITES_UNIT]
                            [--decrease-writes-unit DECREASE_WRITES_UNIT]
                            [--min-provisioned-writes MIN_PROVISIONED_WRITES]
                            [--max-provisioned-writes MAX_PROVISIONED_WRITES]
                            [--num-write-checks-before-scale-down NUM_WRITE_CHECKS_BEFORE_SCALE_DOWN]

    Dynamic DynamoDB - Auto provisioning AWS DynamoDB

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            Read configuration from a configuration file
      --dry-run             Run without making any changes to your DynamoDB table
      --check-interval CHECK_INTERVAL
                            How many seconds should we wait between the checks
                            (default: 300)
      --log-file LOG_FILE   Send output to the given log file
      --log-level {debug,info,warning,error}
                            Log level to use (default: info)
      --log-config-file LOG_CONFIG_FILE
                            Use a custom Python logging configuration file.
                            Overrides both --log-level and --log-file.
      --version             Print current version number
      --aws-access-key-id AWS_ACCESS_KEY_ID
                            Override Boto configuration with the following AWS
                            access key
      --aws-secret-access-key AWS_SECRET_ACCESS_KEY
                            Override Boto configuration with the following AWS
                            secret key

    Daemon options:
      --daemon DAEMON       Run Dynamic DynamoDB in daemon mode. Valid modes are
                            [start|stop|restart|foreground]
      --instance INSTANCE   Name of the Dynamic DynamoDB instance. Used to run
                            multiple instances of Dynamic DynamoDB. Give each
                            instance a unique name and control them separately
                            with the --daemon flag. (default: default)
      --pid-file-dir PID_FILE_DIR
                            Directory where pid file is located in. Defaults to
                            /tmp

    DynamoDB options:
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
      --throttled-reads-upper-threshold THROTTLED_READS_UPPER_THRESHOLD
                            Scale up the reads with --increase-reads-with percent
                            if the count of throttled read events exceeds this
                            count (default: 100)
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
      --increase-reads-unit INCREASE_READS_UNIT
                            Do you want to scale in percent or units? (default:
                            percent)
      --decrease-reads-unit DECREASE_READS_UNIT
                            Do you want to scale in percent or units? (default:
                            percent)
      --min-provisioned-reads MIN_PROVISIONED_READS
                            Minimum number of provisioned reads
      --max-provisioned-reads MAX_PROVISIONED_READS
                            Maximum number of provisioned reads
      --num-read-checks-before-scale-down NUM_READ_CHECKS_BEFORE_SCALE_DOWN
                            Number of consecutive checks that must meet criteria
                            before a scale down event occurs
      --increase-writes-unit INCREASE_WRITES_UNIT
                            Do you want to scale in percent or units? (default:
                            percent)
      --decrease-writes-unit DECREASE_WRITES_UNIT
                            Do you want to scale in percent or units? (default:
                            percent)

    Write units scaling properties:
      --writes-upper-threshold WRITES_UPPER_THRESHOLD
                            Scale up the writes with --increase-writes-with
                            percent if the currently consumed write units reaches
                            this many percent (default: 90)
      --throttled-writes-upper-threshold THROTTLED_WRITES_UPPER_THRESHOLD
                            Scale up the reads with --increase-writes-with percent
                            if the count of throttled write events exceeds this
                            count (default: 100)
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
      --num-write-checks-before-scale-down NUM_WRITE_CHECKS_BEFORE_SCALE_DOWN
                            Number of consecutive checks that must meet criteria
                            before a scale down event occurs