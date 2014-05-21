IAM permissions
===============

If you want to set up a separate IAM user for Dynamic DynamoDB, then you need to grant the user the following privileges:

* ``cloudwatch:GetMetricStatistics``
* ``dynamodb:DescribeTable``
* ``dynamodb:ListTables``
* ``dynamodb:UpdateTable``
* ``sns:Publish`` (used by the SNS notifications feature)

Example IAM policy
------------------

Here's an example IAM policy. Please make sure you update the ARNs according to your needs.
::

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "dynamodb:DescribeTable",
            "dynamodb:ListTables",
            "dynamodb:UpdateTable",
            "cloudwatch:GetMetricStatistics"
          ],
          "Resource": [
            "*"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "sns:Publish"
          ],
          "Resource": [
            "arn:aws:sns:*::dynamic-dynamodb"
          ]
        }
      ]
    }
