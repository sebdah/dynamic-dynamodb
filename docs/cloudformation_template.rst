.. _cloudformation-template:
CloudFormation template
=======================

Overview
--------

To make it as easy as possible to get Dynamic DynamoDB up and running we provide a `CloudFormation <http://aws.amazon.com/cloudformation/>`__ template. This template will launch an t1.micro instance with Dynamic DynamoDB pre-installed. All you need to do is to provide a Dynamic DynamoDB configuration file to use.

Please note that this will be charged towards your AWS account. The cost for a t1.micro server in ``us-east-1`` is less than 15 USD / month.

Setup instructions
------------------

Starting the CloudFormation stack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following will create a new CloudFormation stack. This will launch a new EC2 instance.

1. Download the `Dynamic DynamoDB CloudFormation template <https://raw.github.com/sebdah/dynamic-dynamodb/develop/cloudformation-templates/dynamic-dynamodb.json>`__ to your computer.

2. If you are already using Dynamic DynamoDB and have an existing configuration file, upload it to AWS S3. Take a note of the bucket name and path. You need to call the configuration ``dynamic-dynamodb.conf``.

3. From the `AWS CloudFormation dashboard <https://console.aws.amazon.com/cloudformation/home>`__ click **Create stack**

4. On the **Template page**:

    a. In the **Name** text box, enter the name of the stack. For example: ``DynamicDynamoDB``.

    b. In the **Template** section, click **Upload template file**. Click **Choose File** and select the file you downloaded in step 1.

    c. Click **Next step**.

5. On the **Parameters page**:

    a. In the **S3Bucket** text box, enter a URI for your Amazon S3 bucket. For example: ``s3://bucket-name/dynamic-dynamodb/``.  The URI **must** have a trailing slash (``/``). This should be the same bucket and path as you used in step 2. If you did not upload a template in step 2, choose any S3 bucket and path.

    b. Define the region for the S3 bucket in the **S3BucketRegion** text box. This is needed due to a limitation in the AWS CLI (https://github.com/aws/aws-cli/issues/564).

    c. In the **KeyPair** text box, enter the name of your `Amazon EC2 key pair <https://console.aws.amazon.com/ec2/v2/home?#KeyPairs:>`__

    d. (Optional) Change the instance type. Default is t1.micro.

    e. Click **Next Step**.

6. On the **Options page**, click **Next Step**. There are no tasks to perform on this page.

7. On the **Review page**, review the options for your stack

8. If you are OK with all configuration, click **Create**

CloudFormation will now create your stack, it will take a few minutes. You can follow the progress by watching the **Events** tab on your stack.

Debugging template errors
^^^^^^^^^^^^^^^^^^^^^^^^^

If you need to debug errors in the template setup, you'll want to disable CloudFormation rollbacks. You can do that when you deploy the CloudFormation template in the section above. On the **Options page** (step 6), click **Advanced** and select **No** under **Rollback on failure**.

This will keep the EC2 instance running and allow you to log in and debug any issues you might experience.

Accessing the EC2 instance
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can find your instance in the `EC2 instance list <https://console.aws.amazon.com/ec2/v2/home?#Instances:search=dynamic-dynamodb>`__. The instance name is ``dynamic-dynamodb``.

You can then access the instance via SSH:
::

    ssh -i /path/to/key.pem ec2-user@<hostname>

Updating configuration
^^^^^^^^^^^^^^^^^^^^^^

You can update the configuration directly on the EC2 instance. Simply modify ``/etc/dynamic-dynamodb/dynamic-dynamodb.conf`` and restart Dynamic DynamoDB.

Starting and stopping Dynamic DynamoDB
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dynamic DynamoDB runs in daemon mode on the EC2 instance.

You can start the daemon by running:
::

    service dynamic-dynamodb start

And you can stop it by running:
::

    service dynamic-dynamodb stop

Deleting the stack
------------------

If you wish to remove the CloudFormation stack, follow these steps:

1. From the `AWS CloudFormation dashboard <https://console.aws.amazon.com/cloudformation/home>`__, select your stack.

2. Click **Delete stack** and then **Yes, delete**, when prompted.
