#!/bin/bash

#####
# Bash script to get user info
# call parameters:
#
# user-get username
#####

HOST=mlflow.dev.imagine-ai.eu
USER=$1
echo "Please, enter user password:"
read -s PASS

echo "Getting user info, $USER .."
curl -X GET https://${HOST}/api/2.0/mlflow/users/get?username=${USER} --user "${USER}:${PASS}"
