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
							"lambda.amazonaws.com","apigateway.amazonaws.com"
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
		DependsOn("LambdaExecutionRole")
		Property("Description","This function reads AWS services and builds a html map as output")
		Property("Role",FnGetAtt("LambdaExecutionRole","Arn"))
		Property("FunctionName",lambda_function_name) # Note: lambda_function_name is not defined in this file, it needs to be passed as a -D
		Property("Handler","map.lambda_handler")
		Property("Runtime","python2.7")
		Property("Code", S3Bucket:"sdevenis-lambda", S3Key:"aws-looky-loo.zip")
	end


	## API resources
	ApiGateway_RestApi("RestAPI") do
		Description "Base API Gateway for exposing DMS tasks to customers"
		Property("Description","API acting as a pseudo web server for AWS-html-map-service")
		Name "AWSHtmlMap"
	end

	ApiGateway_Method("MethodRootGET") do
		Property("ApiKeyRequired", "false")
		Property("AuthorizationType", "NONE")
		Property("HttpMethod", "GET")
		Property("Integration", {
			"Type" => "AWS_PROXY",
			#		 "RequestParameters" => { ""])},
			"IntegrationHttpMethod" => "POST",
			"IntegrationResponses" => [
				{ "StatusCode" => "200", "SelectionPattern" => ".*" },
				{ "StatusCode" => "400", "SelectionPattern" => "BAD_REQUEST" },
				{ "StatusCode" => "401", "SelectionPattern" => "NOT_AUTHORISED" },
				{ "StatusCode" => "403", "SelectionPattern" => "FORBIDDEN" },
				{ "StatusCode" => "404", "SelectionPattern" => "TASK_NOT_FOUND" },
				{ "StatusCode" => "500"}
			],
			# Crazy URI required!
			#		 "Uri" => "arn:aws:apigateway:ap-southeast-2:lambda:path/2015-03-31/functions/arn:aws:lambda:ap-southeast-2:726508711480:function:AWS-html-map-service/invocations"
			"Uri" => FnJoin("", ["arn:aws:apigateway:", Ref("AWS::Region"), ":lambda:path/2015-03-31/functions/", FnGetAtt("LambdaAWSMap","Arn"),"/invocations"])
		})
		Property("MethodResponses", [
			{ "StatusCode" => "200", "ResponseModels" => { "application/json" => "Empty" } },
			{ "StatusCode" => "400" },
			{ "StatusCode" => "401" },
			{ "StatusCode" => "403" },
			{ "StatusCode" => "404" },
			{ "StatusCode" => "500" }
		])
		Property("ResourceId",FnGetAtt("RestAPI", "RootResourceId"))
		Property("RestApiId", Ref("RestAPI"))
	end

	Resource("ApiGatewayToLambdaPermission") do
		DependsOn("LambdaAWSMap")
		Type("AWS::Lambda::Permission")
		Property("Action","lambda:InvokeFunction")
		Property("Principal","apigateway.amazonaws.com")
		Property("FunctionName",lambda_function_name) # Note: lambda_function_name is not defined in this file, it needs to be passed as a -D


	end

	ApiGateway_Deployment("Deployment") do
		DependsOn(["MethodRootGET"])
		Property("RestApiId", Ref("RestAPI"))
		Property("StageName", "awshtml")
	end
end
