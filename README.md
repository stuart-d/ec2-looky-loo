# aws-looky-loo

**Overview

A relatively simple tool to help visualise an AWS environment with an html page.
Built with Python, Lambda and API gateway

**Installation (if you just want to run it on AWS):

    install awscli
    configure
    clone
    rake install

**Installation (to run locally or do development work)

    pip install awscli
    pip install boto3
    pip install bs4
    aws configure
    git clone
    rake install
    python -c 'import map; map.lambda_handler("","",debug="true")'

**What services does it show:
* None as yet!


**Things to fix:
* Host css in s3 and permision it open
* Comments and file tidy up
* The initial lambda creation requires a zip on S3, will replace with an inline placeholder
* Modernise the way variables are injected into CFNDSL
