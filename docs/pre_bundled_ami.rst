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


Logging
-------

All logs are available under ``/var/log/dynamic-dynamodb.log``.

The log file is rotated using ``logrotate`` and it is rotated daily. You can
find the logrotation configuration under ``/etc/logrotate.d/dynamic-dynamodb``.
