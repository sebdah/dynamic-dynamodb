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
          "Sid": "Stmt1400661806000",
          "Effect": "Allow",
          "Action": [
            "dynamodb:DescribeTable",
            "dynamodb:ListTables",
            "dynamodb:UpdateTable"
          ],
          "Resource": [
            "arn:aws:dynamodb:us-east-1:123412341234:table/mytable"
          ]
        },
        {
          "Sid": "Stmt1400661929000",
          "Effect": "Allow",
          "Action": [
            "cloudwatch:GetMetricStatistics"
          ],
          "Resource": [
            "*"
          ]
        },
        {
          "Sid": "Stmt1400661943000",
          "Effect": "Allow",
          "Action": [
            "sns:Publish"
          ],
          "Resource": [
            "arn:aws:sns:us-east-1:123412341234:my-topic"
          ]
        }
      ]
    }
