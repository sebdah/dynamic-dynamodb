Pre-bundled AMI
===============

The project provides an `AMI <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html>`__
pre-bundled with Dynamic DynamoDB. It is perfect for running on a t1.micro instance!

The AMI is based on a clean `Ubuntu 13.10 <http://releases.ubuntu.com/saucy/>`__ image.


Launch the AMI
--------------

TODO - More details needed!


Configure Dynamic DynamoDB
--------------------------

The main configuration file is ``/etc/dynamic-dynamodb/dynamic-dynamodb.conf``. The AMI is bundled with the latest example configuration, which you must update to contain your AWS credentials and DynamoDB details.


Managing the daemon
-------------------

Dynamic DynamoDB will be executed as a daemon on the system. You can start and stop it using:
::

    sudo service dynamic-dynamodb {start|stop|status|restart|force-reload}

The daemon is configured to automatically starting and stopping when the instance
is booted or turned off.

Logging
-------

All logs are available under ``/var/log/dynamic-dynamodb.log``.

The log file is rotated using ``logrotate`` and it is rotated daily. You can
find the logrotation configuration under ``/etc/logrotate.d/dynamic-dynamodb``.


Dynamic DynamoDB version
------------------------

The AMI will automatically install the latest version of Dynamic DynamoDB
1.x.x. You can define a custom version number in ``/etc/dynamic-dynamodb/requirements.txt``,
if you want to run a specific version of Dynamic DynamoDB. You can read about the
``requirements.txt`` in the `pip documentation <http://www.pip-installer.org/en/latest/logic.html#requirements-file-format>`__.

Crontab will check for new Dynamic DynamoDB releases every day (see ``/etc/cron.daily``).
