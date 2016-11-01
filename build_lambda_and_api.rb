CloudFormation do
	Description("Creates Lambda function and associated API gateway endpoints for AWS map")
	AWSTemplateFormatVersion("2010-09-09")

	Resource("LambdaExecutionRole") do
	    Type("AWS::IAM::Role")
			Property("Path","/service-role/")
			Property("ManagedPolicyArns",["arn:aws:iam::aws:policy/service-role/AWSLambdaRole",
																		"arn:aws:iam::aws:policy/AWSLambdaExecute",
																		"arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
																		"arn:aws:iam::aws:policy/AmazonVPCReadOnlyAccess"])
	    Property("AssumeRolePolicyDocument", {
	  "Statement" => [
	    {
	      "Action"    => [
	        "sts:AssumeRole"
	      ],
	      "Effect"    => "Allow",
	      "Principal" => {
	        "Service" => [
	          "lambda.amazonaws.com"
	        ]
	      }
	    }
	  ],
	  "Version"   => "2012-10-17"
	})
	    Property("Path", "/")
	  end
Resource("LambdaAWSMap") do
		  Type("AWS::Lambda::Function")
			Property("Description","This function reads AWS services and builds a html map as output")
			Property("Role",FnGetAtt("LambdaExecutionRole","Arn"))
			Property("FunctionName","AWS-html-map-service")
			Property("Handler","map.lambda_handler")
			Property("Runtime","python2.7")
			Property("Code", S3Bucket:"sdevenis-lambda", S3Key:"aws-looky-loo.zip")
	end
end
