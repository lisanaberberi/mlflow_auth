#!/bin/bash

#####
# Bash script to get user info. To be used by ADMIN!
# call parameters:
#
# user-get-as-admin username
#####

HOST=mlflow.dev.imagine-ai.eu
USER=$1
echo "Please, enter **admin** password:"
read -s PASS

echo "Getting user info, $USER .."
curl -X GET https://${HOST}/api/2.0/mlflow/users/get?username=${USER} --user "admin:${PASS}"
