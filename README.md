# ec2-looky-loo

## What is it?

ec2-looky-loo is a simple tool to visualise an AWS EC2 environment as an html page.

It was intended to help with troubleshooting environments and as a general visual reference while not requiring much setup and being cost efficient to run.

## What does it look like?

![Screenshot](/images/example.png)

## What services does it show?
* VPC and Availability zones
* Network ACL's
* EC2 instances

##How is it built and what services does it use to run?

The tool is deployed to AWS Lambda, S3 and API Gateway

* Lambda function is written in python
* CloudFormation defined with Ruby CFNDSL
* Build scripts configured with Ruby Rake

## How much does it cost to run?

The tool deliberately uses an on demand, serverless architecture to keep costs minimal. It doesn't incur any "running costs", its more of a cost per invocation model.

For most people this tool should incur a negligible cost on AWS (i.e. 1c a month)

Assuming 100 page loads a day:

Each time you load an ec2-looky-loo map, you incur:

| Service       | What's used   | $  |Notes
| ------------- |:-------------:| ---------:|----------
| API Gateway   | 3000 HTTP GET | $0     |
| Lambda      | 3000 x invocations  |   $0     |First 1 million requests per month are free (ongoing)
| S3 |  3000 HTTP GETs & 3K storage    |  $.01        |
| API | < 10 calls   |    $0      |API calls are free


More details can be found here:

https://aws.amazon.com/lambda/pricing/
https://aws.amazon.com/api-gateway/pricing/
https://aws.amazon.com/s3/pricing/

NOTE: Remember the AWS Free Tier!

## Installation (if you just want to run it on AWS):

    git clone
    pip install awscli
    aws configure
    vim Rakefile # Edit variables
    rake install

## Installation (to run locally or do development work)

    git clone
    virtualenv ec2-looky-loo
    source ec2-looky-loo/bin/activate
    pip install awscli
    pip install boto3
    pip install bs4
    aws configure
    rake install # Install to AWS
    python -c 'import map; map.lambda_handler("","",debug="true")' # to run locally

## Things to fix and issues:
* Add outputs to cloudformation for the http endpoint
* Add main route tables to routes section (currently only explicitly associated routes)
* The initial lambda creation requires a zip on S3, will replace with an inline placeholder
* Ensure all componenets are removed on uninstall (css file)
* Modernise the way variables are injected into CFNDSL
* Fix variable injection into main file
