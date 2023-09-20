
import mlflow
from mlflow.tracking.client import MlflowClient

import requests
from requests.auth import HTTPBasicAuth

# authenticate as built-in admin user
MLFLOW_TRACKING_USERNAME='admin'
MLFLOW_TRACKING_PASSWORD='<password>' #default is password, must be changed asap

# Remote MLFlow server
MLFLOW_REMOTE_SERVER="http://mlflow.dev.ai4eosc.eu/"

#Set the MLflow server and backend and artifact stores
mlflow.set_tracking_uri(MLFLOW_REMOTE_SERVER)

#initialize an instance to request and query the MLflow server.
client = MlflowClient()


#MLflow Authentication introduces several new API endpoints to manage users and permissions.
# The following routine is about EXPERIMENT permissions, who is allowed to read, edit, manage experiments as mlflow resources

# Define the username you want to manage permissions
username = "username" #insert a username, create first the user by running python create_user.py

# Specify the experiment name you want to retrieve
experiment_name = "<experiment_name>"  # Replace with your experiment name
                                          # e.g. nyc-taxi-exp-prefect

# Make an API request to get experiment object details
def get_experiment_details(experiment_name):
    
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/experiments/get-by-name"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    headers = {'Content-type': 'application/json'}
    params = {'experiment_name': experiment_name}
    response = requests.get(url, auth=auth, headers=headers, params=params)

    experiment = None
    if response.status_code == 200:
        experiment = response.json().get('experiment', {})
        print(f"Experiment Name: {experiment['name']}")
        print(f"Experiment ID: {experiment['experiment_id']}")
        print(f"Artifact Location: {experiment['artifact_location']}")
    else:
        print(f"Failed to retrieve experiments details. Status code: {response.status_code}")

    return experiment


# Create Experiment Permission via API calls
#first define the permissions, among these possilities: READ, EDIT, MANAGE, No_Permission
permission = "MANAGE"
def create_exp_permission(experiment_name, username, permission):
    experiment = get_experiment_details(experiment_name)
    experiment_id = experiment.get('experiment_id')
        # Make an API request to get runs details of the above experiment selected
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/experiments/permissions/create"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    response = requests.post(
    url,
    auth=auth,
    json={
        "experiment_id": experiment_id,
        "username": username,
        "permission": permission
    },
    )       
    if response.status_code == 200:
        data = response.json()
        print(f"Experiment permissions created for the given user. Status code: {response.status_code}")
    elif response.status_code == 400:
        print(f"Resource already exists and only one permission can be assigned to a user for a given exp. Status code: {response.status_code}")
    else:
        print(f"Experiment permission with experiment_id= {experiment_id} and username= {username} not found. Status code: {response.status_code}")      

    return experiment_id, username, permission


# GET EXP permissions, you need an experiment_id (needs to be found based on the name) and username
def get_exp_permission(experiment_name, username):
    
    experiment = get_experiment_details(experiment_name)
    experiment_id = experiment['experiment_id']
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/experiments/permissions/get"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    headers = {'Content-type': 'application/json'}
    params = {'experiment_id': experiment_id,
              'username': username
            }
    response = requests.get(url, auth=auth, headers=headers, params=params)
    print(response.json())
    experiment_permission = None
    if response.status_code == 200:
        experiment_permission = response.json().get('experiment_permission', {})
        print(f"Experiment ID: {experiment_permission['experiment_id']}")
        print(f"User ID: {experiment_permission['user_id']} /username: {username}")
        print(f"Permission_array: {experiment_permission['permission']}")
    else:
        print(f"Failed to retrieve experiment permissions details. Status code: {response.status_code}")

    return experiment_permission

# UPDATE EXP permissions, you need an experiment_id (needs to be found based on the name) and username
permission= "MANAGE"
def udpate_exp_permission(experiment_name, username, permission):
    
    experiment = get_experiment_details(experiment_name)
    experiment_id = experiment['experiment_id']

    #first check what are the current exp permissions to the given user
    get_exp_permission(experiment_name, username)
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/experiments/permissions/update"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    response = requests.patch(
    url,
    auth=auth,
    json={
        "experiment_id": experiment_id,
        "username": username,
        "permission": permission
    },
    )       
    if response.status_code == 200:
        exp_user_perm = response.json()
        print(f"Experiment permission update successful. Status code: {response.status_code}")
    else:
        print(f"Experiment permission with experiment_id= {experiment_id} and username= {username} not found. Status code: {response.status_code}")

    return exp_user_perm


# DELETE EXP Permissions, do not allow a specific user the rights to delete an experiment_id
def delete_exp_permission(experiment_name, username):
    
    experiment = get_experiment_details(experiment_name)
    experiment_id = experiment['experiment_id']

    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/experiments/permissions/delete"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    response = requests.delete(
    url,
    auth=auth,
    json={
        "experiment_id": experiment_id,
        "username": username
    },
    )       
    if response.status_code == 200:
        print(f"Experiment permission delete successful. Status code: {response.status_code}")
    else:
        print(f"Experiment permission delete failed. Status code: {response.status_code}")


# Make an API request to get RUNS details of the above experiment selected
def get_runs_details_of_exp(experiment_name):
    experiment_id = None
    get_runs_details_of_exp = []

    experiment = get_experiment_details(experiment_name)
    print(experiment_name)

    if experiment:
        experiment_id = experiment.get('experiment_id')
        # Make an API request to get runs details of the above experiment selected
        url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/runs/search"
        auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
        response = requests.post(
        url,
        auth=auth,
        json={
            "experiment_ids": [str(experiment['experiment_id'])],
        },
        )       
        if response.status_code == 200:
            data = response.json()
            runs = data.get("runs")
            if runs:
                for run in runs:
                    run_id = run.get("info").get("run_id")
                    print(f"Run ID: {run_id}")
                    # Other run details can be accessed here if needed
            else:
                print(f"No runs found for the specified experiment. Status code: {response.status_code}")
        else:
            print(f"Failed to retrieve runs details. Status code: {response.status_code}")       
    else:
        print("No experiment details found. Status code")

    return experiment_id, runs

#usage

create_exp_permission(experiment_name, username, permission)
#get_exp_permission(experiment_name,username)
udpate_exp_permission(experiment_name, username, permission)
delete_exp_permission(experiment_name, username)


#Usage --2nd part in listing all runs of an exp and check auth against a run_id
experiment_id, runs = get_runs_details_of_exp(experiment_name)

selected_run_index = int(input("Select a run (enter the number, not the ID): ")) -1
run_uuid=None
if 0 <= selected_run_index < len(runs):
    selected_run_id = runs[selected_run_index]
    run_uuid = selected_run_id['info']['run_uuid']
    print(f"Selected Run ID: {selected_run_id}")
else:
    print("Invalid selection. Please enter a valid run number.")


print(" Start checking the authentication of a specific run")
# test authentication first of a specific run-id of an existing experiment
def test_authentication(run_uuid):

    auth=HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/runs/get"
    headers = {'content-type': 'application/json'}
    params = {'run_id' : run_uuid}
    response = requests.get(url, auth=auth, headers=headers, params=params)
    response.json()
    if response.status_code == 200:
        print("Authentication successful")
    else:
        print("Authentication failed")

test_authentication(run_uuid)