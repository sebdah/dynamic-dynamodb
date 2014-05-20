IAM permissions
===============

If you want to set up a separate IAM user for Dynamic DynamoDB, then you need to grant the user the following privileges:

* ``cloudwatch:GetMetricStatistics``
* ``dynamodb:DescribeTable``
* ``dynamodb:ListTables``
* ``dynamodb:UpdateTable``
* ``sns:Publish`` (used by the SNS notifications feature)
