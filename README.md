# ec2-looky-loo

## What is it?

ec2-looky-loo is a simple tool to visualise an AWS EC2 environment as an html page.

It was intended to help with troubleshooting environments and as a general visual reference while not requiring much setup and being cost efficient to run.

## What does it look like?

![Screenshot](/images/example.png)

## How does it work?

The architecture is as follows:

![Architecture](/images/diagram.png)

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

For most people this tool should incur a negligible cost on AWS (i.e. <5c a month)

Monthly estimate assuming 100 page loads a day (and not considering free tier):

| Service       | What's used   | $  |Notes
| ------------- |-------------| ---------:|----------
| API Gateway   | 3000 HTTP GET | $0.01     |https://aws.amazon.com/api-gateway/pricing/
| Lambda      | 3000 x invocations  |   $0     |https://aws.amazon.com/lambda/pricing/
| S3 |  3000 HTTP GETs & 3K storage    |  $0.01        |https://aws.amazon.com/s3/pricing/
| API | ~ 30K calls   |    $0      |API calls are free

## Deploying / Undeploying (if you just want to run it on AWS):

    git clone
    Install and configure awscli
    Edit .activate.sh
    . .activate.sh
    packagecode
    deploycode
    create
    status
    output
    delete
    deletecode


*Note: You will need the appropriate AWS permissions to create all the resources*    

## Installation (to run locally or do development work)

    python -c 'import map; map.lambda_handler("","",debug="true")' # to run locally

*Note: You will need the appropriate AWS permissions to create all the resources*    

## Things to fix and issues:
* Add RDS support
* Add NAT / IGW support
* Add ECS
* Modernise the way variables are injected into CFNDSL
* Fix variable injection into main file
