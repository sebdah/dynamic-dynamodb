Dynamic DynamoDB on Amazon AWS Lambda
=====================================

Setup Amazon AWS Stack
----------------------

1. Copy `example-dynamic-dynamodb.conf` to `dynamic-dynamodb.conf` and set your settings.

2. Create some S3 bucket.

3. Create lambda package and upload to S3 bucket:
::

    ./setup-lambda.sh $S3_BUCKET_NAME

4. Create lambda stack:
::

    aws cloudformation create-stack --stack-name $STACK_NAME \
        --capabilities CAPABILITY_IAM \
        --template-body file://cloudformation-templates/dynamic-dynamodb-lambda.json \
        --parameters ParameterKey=S3Bucket,ParameterValue=$S3_BUCKET_NAME \
        ParameterKey=S3Key,ParameterValue=dynamic-dynamodb-lambda.zip

Update Amazon AWS stack
-----------------------

::

    aws cloudformation update-stack --stack-name $STACK_NAME \
        --capabilities CAPABILITY_IAM \
        --template-body file://cloudformation-templates/dynamic-dynamodb-lambda.json \
        --parameters ParameterKey=S3Bucket,ParameterValue=$S3_BUCKET_NAME \
        ParameterKey=S3Key,ParameterValue=dynamic-dynamodb-lambda.zip

Update Lambda Function Code
---------------------------

After you've created the stack, you can get lambda function name:
::

    LAMBDA_NAME=$(aws cloudformation describe-stack-resource --stack-name $STACK_NAME --logical-resource-id LambdaFunction --query 'StackResourceDetail.PhysicalResourceId' --output text)

Update lambda code by running helper script:
::

    ./setup-lambda.sh $S3_BUCKET_NAME $LAMBDA_NAME

Scheduled Events
----------------

After lambda function is created you can create Scheduled Events (aka cron events). Currently only from AWS Web Console.
