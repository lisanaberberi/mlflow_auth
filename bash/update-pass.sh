#!/bin/bash

#####
# Bash script for users to update their own passwords
# (admin can also update his/er own password
# call parameters:
#
# update-pass username
#####

HOST=mlflow.dev.imagine-ai.eu
USER=$1
echo "Please, enter current password:"
read -s OLDPASS
echo "Enter new password:"
read -s NEWPASS

echo "Updating password for $USER .."
curl -X PATCH https://${HOST}/api/2.0/mlflow/users/update-password -H "Content-Type: application/json" -d '{"username":"'"${USER}"'", "password":"'"${NEWPASS}"'"}' --user "${USER}:${OLDPASS}"
