#!/usr/bin/env bash
#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 - 2023 Karlsruhe Institute of Technology - Steinbuch Centre for Computing
# This code is distributed under the MIT License
# Please, see the LICENSE file
#
# @author: vykozlov

###
# bash script to create, update, and manage a user
# every function intentionally asks every time for 
# USER and PASS
# to avoid accidental failures as deleting users etc
###

# load variable from .env
SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"
[[ -f "${SCRIPT_PATH}/.env" ]] && source ${SCRIPT_PATH}/.env || MLFLOW_HOST="http://localhost"
[[ -f "${SCRIPT_PATH}/VERSION" ]] && source ${SCRIPT_PATH}/VERSION || VERSION="0.1.0"

function usage()
{
    shopt -s xpg_echo
    echo "\nbash script to create, update, and manage a user\n
    Usage: $0 <option> \n
    Options (only ONE option at the time!):
    -h|--help \t\t\t the help message
    -c|--create \t\t create a new <user>
    -d|--delete \t\t delete <user>
    -g|--get \t\t\t get <user> info
       --get-as-admin \t\t get <user> info being an admin
    -p|--update-pass \t\t update <user>'s password
       --is-admin \t\t make <user> admin
       --not-admin \t\t remove admin status from the <user>
    -u|--user <user> \t\t provide <user> for create/delete/get/update operations (has to be before the operation!)
    -v|--version \t\t get scripts version" 1>&2; exit 0;
}

function create-user()
{   echo "Creating new user, $USER .."
    echo "Please, enter **admin** password:"
    read -s ADMINPASS
    echo "Please, enter initial user's password:"
    read -s PASS

    curl -X POST ${MLFLOW_HOST}/api/2.0/mlflow/users/create -H "Content-Type: application/json" -d '{"username":"'"${USER}"'", "password":"'"${PASS}"'"}' --user "admin:${ADMINPASS}"
}

function delete-user()
{   echo "DELETING user: $USER .."
    read -p "Are you sure you want to delete user: ${USER}? (Y/N)" -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo "Please, enter **admin** password:"
        read -s ADMINPASS
        curl -X DELETE ${MLFLOW_HOST}/api/2.0/mlflow/users/delete -H "Content-Type: application/json" -d '{"username":"'"${USER}"'"}' --user "admin:${ADMINPASS}"
    fi
}

function get-user()
{   echo "Getting user info, $USER .."
    echo "Please, enter user's password ($USER):"
    read -s PASS
    curl -X GET ${MLFLOW_HOST}/api/2.0/mlflow/users/get?username=${USER} --user "${USER}:${PASS}"
}

function get-user-as-admin()
{   echo "Getting user info, $USER, (as admin).."
    echo "Please, enter **admin** password:"
    read -s ADMINPASS
    curl -X GET ${MLFLOW_HOST}/api/2.0/mlflow/users/get?username=${USER} --user "admin:${ADMINPASS}"
}

function update-pass()
{   echo "Updating password for $USER .."
    echo "Please, enter current password:"
    read -s OLDPASS
    echo "Enter new password:"
    read -s NEWPASS

    curl -X PATCH ${MLFLOW_HOST}/api/2.0/mlflow/users/update-password -H "Content-Type: application/json" -d '{"username":"'"${USER}"'", "password":"'"${NEWPASS}"'"}' --user "${USER}:${OLDPASS}"
}

function update-admin()
{   adminstatus=$1
    [[ "$adminstatus" = true ]] && echo "Making user, $USER, admin .." || echo "Removing admin status from the user, $USER, .."
    echo "Please, enter **admin** password:"
    read -s ADMINPASS
    curl -X PATCH ${MLFLOW_HOST}/api/2.0/mlflow/users/update-admin -H "Content-Type: application/json" -d '{"username":"'"${USER}"'", "is_admin":'${adminstatus}'}' --user "admin:${ADMINPASS}"
}

function check_arguments()
{
    OPTIONS=hcgdpu:v
    LONGOPTS=help,create,get,get-as-admin,delete,update-pass,is-admin,not-admin,user:,version
    # https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
    # saner programming env: these switches turn some bugs into errors
    #set -o errexit -o pipefail -o noclobber -o nounset
    set  +o nounset
    ! getopt --test > /dev/null
    if [[ ${PIPESTATUS[0]} -ne 4 ]]; then
        echo '`getopt --test` failed in this environment.'
        exit 1
    fi

    # -use ! and PIPESTATUS to get exit code with errexit set
    # -temporarily store output to be able to check for errors
    # -activate quoting/enhanced mode (e.g. by writing out “--options”)
    # -pass arguments only via   -- "$@"   to separate them correctly
    ! PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
    if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
        # e.g. return value is 1
        #  then getopt has complained about wrong arguments to stdout
        exit 2
    fi
    # read getopt’s output this way to handle the quoting right:
    eval set -- "$PARSED"

    if [ "$1" == "--" ]; then
        echo "[INFO] No arguments provided!"
        usage
        exit 1
    fi

    # now enjoy the options in order and nicely split until we see --
    while true; do
        case "$1" in
            -h|--help)
                usage
                break
                ;;
            -c|--create)
                create-user
                shift
                ;;
            -d|--delete)
                delete-user
                shift
                ;;
            -g|--get)
                get-user
                shift
                ;;
            --get-as-admin)
                get-user-as-admin
                shift
                ;;
            -p|--update-pass)
                update-pass
                shift
                ;;
            --is-admin)
                update-admin true
                shift
                ;;
             --not-admin)
                update-admin false
                shift
                ;;
             -u|--user)
                USER="$2"
                shift 2
                ;;        
            -v|--version)
                echo "Version of the bash scripts: $VERSION"
                exit 0
                ;;
            --)
                shift
                break
                ;;
            *)
                break
                ;;
        esac
    done
}

check_arguments "$0" "$@"