CloudFormation do
	Description("Creates Lambda function and associated API gateway endpoints for AWS map")
	AWSTemplateFormatVersion("2010-09-09")

	Resource("LambdaExecutionRole") do
	    Type("AWS::IAM::Role")
			Property("Path","/service-role/")
			Property("ManagedPolicyArns",["arn:aws:iam::aws:policy/AWSLambdaExecute",
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

#		Resource("RolePolicies") do
#	    Type("AWS::IAM::Policy")
#	    Property("PolicyName", "root")
#	    Property("PolicyDocument", {
#	  "Statement" => [
#	    {
#	      "Action"   => "*",
#	      "Effect"   => "Allow",
#	      "Resource" => "*"
#	    }
#	  ],
#	  "Version"   => "2012-10-17"
#	})
#	    Property("Roles", [
#	  Ref("LambdaExecutionRole")
#	])
#	  end
end
