# This rakefile builds

project_dir = Dir.pwd
tool_name = "ec2-looky-loo"
cfn_stack_name = "ec2-looky-loo"
cfndsl_rb = "cloudformation.rb"
cfndsl_template = "cloudformation.template"
lambda_function_name = "ec2-looky-loo"
lambda_code_zip = project_dir + "/" + tool_name + ".zip"
required_python_pkgs = ["bs4"]

task :default => [:help]
task :install => [:cfn_create_stack,:lambda_update_running_code,:lambda_update_css]
task :updateall => [:cfn_update_stack,:lambda_update_running_code,:lambda_update_css]
task :updatelambda => [:lambda_update_running_code,:lambda_update_css]
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

task :lambda_update_running_code => [:lambda_create_code_zipfile] do
  run_cmds(["aws lambda update-function-code --function-name " +  lambda_function_name + " --zip fileb://" + lambda_code_zip])
end

task :lambda_update_css do
  run_cmds(["aws s3 cp main.css s3://sdevenis-lambda/ --storage-class REDUCED_REDUNDANCY --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers"])
end

def run_cmds(commands)
  commands.each { |cmd|
  print ("Running: " + cmd + "\n")
  print ("----- Begin output ------\n")
  system(cmd)
  print ("----- End output ------\n")
  }
end
