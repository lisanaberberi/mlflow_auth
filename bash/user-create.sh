#!/bin/bash

#####
# Bash script to create a new user. ONLY admin can do this!
# call parameters:
#
# user-create username
#####

HOST=mlflow.dev.imagine-ai.eu
USER=$1
echo "Please, enter **admin** password:"
read -s ADMINPASS
echo "Please, enter initial user password:"
read -s PASS

echo "Creating new user, $USER .."
curl -X POST https://${HOST}/api/2.0/mlflow/users/create -H "Content-Type: application/json" -d '{"username":"'"${USER}"'", "password":"'"${PASS}"'"}' --user "admin:${ADMINPASS}"
