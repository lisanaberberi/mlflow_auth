
import mlflow
from mlflow.tracking.client import MlflowClient

import requests
from requests.auth import HTTPBasicAuth

from mlflow.entities import ViewType


# authenticate as built-in admin user
MLFLOW_TRACKING_USERNAME='admin'
MLFLOW_TRACKING_PASSWORD='Pti0L4hWVheubbVeegGC' #default is password, must be changed asap

# Remote MLFlow server
MLFLOW_REMOTE_SERVER="http://mlflow.dev.ai4eosc.eu/"


#Set the MLflow server and backend and artifact stores
mlflow.set_tracking_uri(MLFLOW_REMOTE_SERVER)


client = MlflowClient()


# Specify the experiment name you want to retrieve
experiment_name = "nyc-taxi-exp-prefect"  # Replace with your experiment name


def print_run_info(runs):
    for r in runs:
        print(f"run_id: {r.info.run_id}")
        print(f"lifecycle_stage: {r.info.lifecycle_stage}")
        print(f"metrics: {r.data.metrics}")

        # Exclude mlflow system tags
        tags = {k: v for k, v in r.data.tags.items() if not k.startswith("mlflow.")}
        print(f"tags: {tags}")

    # get the experiment
    experiment_id = '59'

    # Search all runs under experiment id and order them by
    # descending value of the metric 'm'
    client = MlflowClient()
    runs = client.search_runs(experiment_id, order_by=["metrics.m DESC"])
    print_run_info(runs)
    print("--")



# Make an API request to get experiment details
url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/experiments/get-by-name"
auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
headers = {'Content-type': 'application/json'}
params = {'experiment_name': experiment_name}
response = requests.get(url, auth=auth, headers=headers, params=params)

print("url", url)

if response.status_code == 200:
    experiment = response.json().get('experiment', {})
    print(f"Experiment Name: {experiment['name']}")
    print(f"Experiment ID: {experiment['experiment_id']}")
    print(f"Artifact Location: {experiment['artifact_location']}")

    # Make an API request to get runs details
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
            print("No runs found for the specified experiment.")
    else:
        print(f"Failed to retrieve runs details. Status code: {response.status_code}")
else:
    print(f"Failed to retrieve experiments details. Status code: {response.status_code}")



# test auth first of a specific run-id of an existing experiment

auth=HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/runs/get"
print("url", url)
headers = {'content-type': 'application/json'}
params = {'run_id' : run_id}
response = requests.get(url, auth=auth, headers=headers, params=params)
response.json()

print("url", url)

if response.status_code == 200:
    print("Authentication successful")
else:
    print("Authentication failed")

#1. First method to create new users (only READ permission) via API call

response_user_1 = requests.post(
    "http://mlflow.dev.ai4eosc.eu/api/2.0/mlflow/users/create",
    auth=auth,
    json={
        "username": "mlflow_u",
        "password": "Pti0L4hWVheubbVeegGC",
    },
)
if response_user_1.status_code == 200:
    print("New User addition successful")
else:
    print("New User addition failed")


# 1.2 Update a user as an admin user using PATCH
response_user_admin = requests.patch(
    "http://mlflow.dev.ai4eosc.eu/api/2.0/mlflow/users/update-admin",
    auth=auth,
    json={
        "username": "mlflow_u",
        "is_admin": 1,
    },
)
if response_user_admin.status_code == 200:
    print("User update successful")
else:
    print("User update failed")


# 1.3 Update admin password using PATCH
response_user_admin = requests.patch(
    "http://mlflow.dev.ai4eosc.eu/api/2.0/mlflow/users/update-password",
    auth=auth,
    json={
        "username": "admin",
        "password": "Pti0L4hWVheubbVeegGC",
    },
)
if response_user_admin.status_code == 200:
    print("Password update successful")
else:
    print("Password update failed")


# # Second method to create new users (only READ permission) via get_app_client()
# from mlflow.server import get_app_client

# auth_client = get_app_client("basic-auth", tracking_uri=url)
# auth_client.create_user(username="user2", password="pass123?")

# # change from user with read only to admin(full permissions)
# auth_client.update_user_admin(username="user2", is_admin=True)

# # For a specific experiment assign permissions to a user
# experiment_id = client.create_experiment(name="experiment_users_manag")

# auth_client.create_experiment_permission(
#     experiment_id=experiment_id, username="user2", permission="MANAGE"
# )
