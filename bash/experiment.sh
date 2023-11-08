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
# bash to manage experiment permissions
###

# load variable from .env
SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"

# need to remove local linux user setting
unset USER
# load version from VERSION file
[[ -f "${SCRIPT_PATH}/VERSION" ]] && source ${SCRIPT_PATH}/VERSION || VERSION="0.1.0"

# load variables from .env
if [[ -f "${SCRIPT_PATH}/.env" ]]; then
   source ${SCRIPT_PATH}/.env
else
   MLFLOW_HOST=http://localhost
   echo "Username:"
   read MLFLOW_USER

   echo "Please, enter user password:"
   read -s MLFLOW_PASS
fi

function usage()
{
    shopt -s xpg_echo
    echo "\nbash script to manage experiment permissions\n
    Usage: $0 <option> \n
    Options (only ONE option at the time!):
    -h|--help \t\t\t the help message
       --create-permissions \t create <permissions> for the experiment <id> and <user>, e.g.
                            \t   $0 -e <id> -u <user> -p <permissions> --create-permissions
       --delete-permissions \t delete experiment <id> permissions for <user>, e.g.
                            \t   $0 -e <id> -u <user> --delete-permissions
    -e|--exp-id \t\t provide experiment <id> for get/create/update permissions (has to be before the operation!)
    -g|--get \t\t\t get experiment info by its <id>, e.g. $0 -e <id> --get
       --get-by-name <name> \t get experiment info by its <name>
       --get-permissions \t get experiment permissions by its <id>, e.g.
                         \t   $0 -e <id> -u <user> --get-permissions
    -p|--permissions \t <permissions> to be set (READ|EDIT|MANAGE|NO_PERMISSIONS) (has to be before the operation!)
       --update-permissions \t update <permissions> for the experiment <id> and <user>, e.g.
                            \t   $0 -e <id> -u <user> -p <permissions> --update-permissions
    -u|--user <user> \t\t provide <user> for which to get/create/update/delete permissions (has to be before the operation!)
    -v|--version \t\t get scripts version" 1>&2; exit 0;
}


function get-by-id()
{   echo "Getting experiment info, $ID .."
    curl -X GET ${MLFLOW_HOST}/api/2.0/mlflow/experiments/get?experiment_id=${ID} --user "${MLFLOW_USER}:${MLFLOW_PASS}"
}

function get-by-name()
{   echo "Getting experiment info, $EXP_NAME .."
    curl -X GET ${MLFLOW_HOST}/api/2.0/mlflow/experiments/get-by-name?experiment_name=${EXP_NAME} --user "${MLFLOW_USER}:${MLFLOW_PASS}"
}

function create-permissions()
{   [[ -z "${USER}" ]] && USER=${MLFLOW_USER} || echo -n ""
    echo "Creating experiment permission, $ID, for user, $USER .."
    curl -X POST ${MLFLOW_HOST}/api/2.0/mlflow/experiments/permissions/create -H "Content-Type: application/json" -d '{"experiment_id":"'"${ID}"'","username":"'"${USER}"'", "permission":"'"${PERMISSION}"'"}' --user "${MLFLOW_USER}:${MLFLOW_PASS}"
}

function get-permissions()
{   [[ -z "${USER}" ]] && USER=${MLFLOW_USER} || echo -n ""
    echo "Getting experiment permissions, $ID, and user, $USER .."
    curl -X GET ''${MLFLOW_HOST}'/api/2.0/mlflow/experiments/permissions/get?experiment_id='${ID}'&username='${USER}'' --user "${MLFLOW_USER}:${MLFLOW_PASS}"
}

function update-permissions()
{   [[ -z "${USER}" ]] && USER=${MLFLOW_USER} || echo -n ""
    echo "Updating experiment permission, $ID, for user, $USER .."
    curl -X PATCH ${MLFLOW_HOST}/api/2.0/mlflow/experiments/permissions/update -H "Content-Type: application/json" -d '{"experiment_id":"'"${ID}"'","username":"'"${USER}"'", "permission":"'"${PERMISSION}"'"}' --user "${MLFLOW_USER}:${MLFLOW_PASS}"
}

function delete-permissions()
{   [[ -z "${USER}" ]] && USER=${MLFLOW_USER} || echo -n ""
    echo "Deleting experiment permission, $ID, for user, $USER .."
    curl -X DELETE ${MLFLOW_HOST}/api/2.0/mlflow/experiments/permissions/delete -H "Content-Type: application/json" -d '{"experiment_id":"'"${ID}"'","username":"'"${USER}"'"}' --user "${MLFLOW_USER}:${MLFLOW_PASS}"
}

function check_arguments()
{
    OPTIONS=he:gp:u:v
    LONGOPTS=help,create-permissions,delete-permissions,exp-id:,get,get-by-name:,get-permissions,permissions:,update-permissions,user:,version
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
            --create-permissions)
                create-permissions
                shift
                ;;
            --delete-permissions)
                delete-permissions
                shift
                ;; 
            -e|--exp-id)
                ID="$2"
                shift 2
                ;;
            -g|--get)
                get-by-id
                break
                ;;
            --get-by-name)
                EXP_NAME="$2"
                get-by-name
                break
                ;;
            --get-permissions)
                get-permissions
                shift
                ;;
            -p|permissions)
                PERMISSION="$2"
                shift 2
                ;;
            --update-permissions)
                update-permissions
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