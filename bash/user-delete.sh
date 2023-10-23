#!/bin/bash

#####
# Bash script to create a new user. ONLY admin can do this!
# call parameters:
#
# user-delete username
#####

HOST=mlflow.dev.imagine-ai.eu
USER=$1
echo "Please, enter **admin** password:"
read -s ADMINPASS

read -p "Are you sure you want to delete user: ${USER}? (Y/N)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "DELETING user: $USER .."
    curl -X DELETE https://${HOST}/api/2.0/mlflow/users/delete -H "Content-Type: application/json" -d '{"username":"'"${USER}"'"}' --user "admin:${ADMINPASS}"
fi
