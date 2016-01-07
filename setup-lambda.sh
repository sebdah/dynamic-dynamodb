#!/usr/bin/env bash

S3_BUCKET_NAME="$1"
LAMBDA_FUNCTION_NAME="$2"

# Install requirements
pip install -r requirements.txt --target ./package
rm -rf ./package/*.dist-info
rm -rf ./package/*.egg-info

# Copy project files
cp -r ./dynamic_dynamodb ./package/
cp ./lambda.py ./package/
cp ./dynamic-dynamodb.conf ./package/

# Create package archive
rm dynamic-dynamodb-lambda.zip
pushd package && zip -qr -MM ../dynamic-dynamodb-lambda.zip . && popd

# Upload to AWS S3 bucket
aws s3 cp dynamic-dynamodb-lambda.zip s3://${S3_BUCKET_NAME}

# Update lambda function code
if [ ! -z ${LAMBDA_FUNCTION_NAME} ]; then
    aws lambda update-function-code --s3-bucket ${S3_BUCKET_NAME} \
        --s3-key dynamic-dynamodb-lambda.zip \
        --function-name ${LAMBDA_FUNCTION_NAME}
fi
