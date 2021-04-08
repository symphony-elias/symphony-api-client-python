#!/usr/bin/env bash

template_dir=`pwd`
project_root=$template_dir/..

echo $template_dir

generate_files() {
  file_url=$1
  file_name=${file_url##*/}
  name=$2
  output_folder=output_${name}

  echo $file_url
  echo $file_name
  echo $name
  echo $output_folder
  # download and generate files
  cd $template_dir


  wget $file_url
  java -jar openapi-generator-cli.jar generate -g python -i $file_name --package-name symphony.bdk.gen -o $output_folder

  # update api files
  cd $template_dir/$output_folder/symphony/bdk/gen/api/
  sed -i ".bak" "s/symphony\.bdk\.gen\.model\./symphony\.bdk\.gen\.${name}_model\./g" *.py
  sed -i ".bak" "s/ api\./ ${name}_api\./g" *.py
  rm __init__.py  # we don't care about __init__.py files
  cp *.py $project_root/symphony/bdk/gen/${name}_api

  # update model files
  cd $template_dir/$output_folder/symphony/bdk/gen/model/
  sed -i ".bak" "s/symphony\.bdk\.gen\.model\./symphony\.bdk\.gen\.${name}_model\./g" *.py
  sed -i ".bak" "s/model /${name}_model /g" *.py
  rm __init__.py  # we don't care about __init__.py files
  cp *.py $project_root/symphony/bdk/gen/${name}_model
}

# agent
generate_files https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/master/agent/agent-api-public.yaml agent

# auth
generate_files https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/master/authenticator/authenticator-api-public.yaml auth

# login
generate_files https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/master/login/login-api-public.yaml login

# pod
generate_files https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/master/pod/pod-api-public-deprecated.yaml pod
