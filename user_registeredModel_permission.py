import os
import mlflow
from mlflow.tracking.client import MlflowClient
from mlflow.server import get_app_client

import requests
from requests.auth import HTTPBasicAuth

from pprint import pprint

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
# The following routine is about REGISTERED_MODEL permissions, 
# who is allowed to read, edit, manage models as mlflow resources

# Define the username you want to manage permissions
username = "mlflow_u"
# Define the permissions, among these possilities: READ, EDIT, MANAGE, No_Permission
permission = "EDIT"

# Specify the model name you want to retrieve from the model repository
model_name = "<model_name>"  # Replace with your model name
                                          # e.g. nyc_taxi

#1. first 
def search_model_all():
#first make sure you have setup the environment vars to authenticate to the server
    for rm in client.search_registered_models():
        pprint(dict(rm), indent=4)


# Make an API request to get registered model object details
def search_model_API():
    
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/registered-models/search"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    headers = {'Content-type': 'application/json'}
    params = {
    "filter": f"name LIKE '%'",  # Modify this to filter by your desired criteria or 
                                              # or by a specific model_name: f"name LIKE '%{model_name}%'"
    "max_results": 4,    # Modify as needed
    "order_by": ["timestamp DESC"],  # You can change the sorting order if needed
    "page_token": None  # Use this to paginate through results if there are many models
    } 
    response = requests.get(url, auth=auth, headers=headers, params=params)
   
    registered_models = None
    if response.status_code == 200:
        registered_models = response.json().get('registered_models', {})
        for model in registered_models:  #An array of RegisteredModels
            last_update_ts = model.get('last_updated_timestamp')
            latest_version = model.get('latest_versions')
            for version in latest_version:
                source_uri = version.get('source')
                run_id = version.get('run_id')
                user_id = version.get('user_id')
                print(f"Last Update Timestamp: {last_update_ts}")
                print(f"Latest Version: {latest_version}")
                print(f"Source artifact uri: {source_uri}")
                print(f"Run ID: {run_id}")   
                print(f"User ID: {user_id}")              
        print(f"Next page token: {response.json().get('next_page_token')}")
    else:
        print(f"Failed to retrieve experiments details. Status code: {response.status_code}")

    return registered_models


# Make an API request to get registered model object details
def get_model_details(model_name):
    
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/registered-models/get"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    headers = {'Content-type': 'application/json'}
    params = {'name': model_name}
    response = requests.get(url, auth=auth, headers=headers, params=params)

    registered_model = None
    if response.status_code == 200:
        registered_model = response.json().get('registered_model', {})
        print(f"Last Update TS: {registered_model['last_updated_timestamp']}")
        print(f"Latest Version: {registered_model['latest_versions']}")
    else:
        print(f"Failed to retrieve experiments details. Status code: {response.status_code}")

    return registered_model

# Create RegisteredModel Permission via API calls
def create_regModel_permission(model_name, username, permission):
    #registeredModel = get_model_details(model_name)
        # Make an API request to give rights to a reg model
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/registered-models/permissions/create"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    response = requests.post(
    url,
    auth=auth,
    json={
        "name": model_name,
        "username": username,
        "permission": permission
    },
    )    
    print(response.json())   
    if response.status_code == 200:
        data = response.json()
        print(f"Permission= {permission} has been given to user={username} for the registered model={model_name}. "
                 f"Status code: {response.status_code}")
    elif response.status_code == 400:
        print(f"Resource already exists and only one permission can be assigned to a user for a given model."
              f"Status code: {response.status_code}")
    else:
        print(f"Registered Model permission of model_name= {model_name} and username= {username} not found."
              f"Status code: {response.status_code}")      

    return model_name, username, permission

#usage
def main():
    search_model_all()
    create_regModel_permission(model_name, username, permission)
    #search_model_API()
    get_model_details(model_name)


if __name__ == '__main__':
    main()