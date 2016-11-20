# Use this rakefil to manage ec2-looky-loo

# Variables you may want to change
tool_name = "ec2-looky-loo"
cfn_stack_name = tool_name
lambda_function_name = tool_name
lambda_css_s3_bucket="s3://sdevenis-lambda/" # Ensure you keep this format with s3:// prefix and / suffix

# Variables you probably won't change
project_dir = Dir.pwd
cfndsl_rb = "cloudformation.rb"
cfndsl_template = "cloudformation.template"
lambda_code_zip = project_dir + "/" + tool_name + ".zip"
required_python_pkgs = ["bs4"]

# Main tasks
task :default => [:help]
desc "Install ec2-looky-loo"
task :install => [:cfn_create_stack,:lambda_update_running_code,:lambda_update_css]
desc "Update entire stack including code and css"
task :update_all => [:cfn_update_stack,:lambda_update_running_code,:lambda_update_css]
desc "Update lambda and css"
task :update_lambda => [:lambda_update_running_code,:lambda_update_css]
desc "Show current stack (including URL of deployment)"
task :display => [:display_cfn_stack]
desc "Uninstall everything"
task :uninstall => [:delete_cfn_stack]

task :cfn_generate do
  Dir.chdir project_dir
  run_cmds(["ruby-beautify --overwrite " + cfndsl_rb,
           "cfndsl -p -D \"lambda_function_name=\'" + lambda_function_name + "\'\" " + cfndsl_rb + " > " + cfndsl_template])
end

task :lambda_create_code_zipfile do
  print "Creating deployment package: " + lambda_code_zip + "\n"
  run_cmds(["zip -9 " + lambda_code_zip + " ./map.py"])

  Dir.chdir ("lib/python2.7/site-packages/")
  required_python_pkgs.each { |package|
    run_cmds(["zip -r9 " + lambda_code_zip + " ./" + package])
  }
  Dir.chdir (project_dir)
end

task :help do
  print "HELP!\n"
end

task :cfn_create_stack => [:cfn_generate] do
  run_cmds(["aws cloudformation create-stack --stack-name " + cfn_stack_name + " --template-body file://" + project_dir + "/" + cfndsl_template + " --capabilities CAPABILITY_IAM",
            "aws cloudformation wait stack-create-complete --stack-name " + cfn_stack_name])
end

task :cfn_update_stack => [:cfn_generate] do
  run_cmds(["aws cloudformation update-stack --stack-name " + cfn_stack_name + " --template-body file://" + project_dir + "/" + cfndsl_template + " --capabilities CAPABILITY_IAM",
            "aws cloudformation wait stack-update-complete --stack-name " + cfn_stack_name])
end

task :delete_cfn_stack do
  run_cmds(["aws cloudformation delete-stack --stack-name " + cfn_stack_name,
            "aws cloudformation wait stack-delete-complete --stack-name " + cfn_stack_name])
end

task :display_cfn_stack do
  run_cmds(["aws cloudformation describe-stacks --stack-name " + cfn_stack_name])
end

task :lambda_update_running_code => [:lambda_create_code_zipfile] do
  run_cmds(["aws lambda update-function-code --function-name " +  lambda_function_name + " --zip fileb://" + lambda_code_zip])
end

task :lambda_update_s3_code => [:lambda_create_code_zipfile] do
  run_cmds(["aws s3 cp " + lambda_code_zip + " " + lambda_css_s3_bucket] +" --storage-class REDUCED_REDUNDANCY")
end

task :lambda_update_css do
  run_cmds(["aws s3 cp main.css " + lambda_css_s3_bucket +" --storage-class REDUCED_REDUNDANCY --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers"])
end

def run_cmds(commands)
  commands.each { |cmd|
    print ("Running: " + cmd + "\n")
    print ("----- Begin output ------\n")
    system(cmd)
    print ("----- End output ------\n")
#    if $? != 0
#      print ("Command failed, exit code was" + $?.exitstatus)
#    end
  }
end
