
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

# Define your authentication credentials
auth = HTTPBasicAuth("admin", "<password>")

# Define the username and password for the new user
new_user_username = "ubuntu"
new_user_password = "pass"  #type a new password

# Define the new password of an existing user(admin)
user_password = "pass" #type a new password

# Define the user you want to delete
user_to_delete="mlflow_u"

# Create a new user
def create_new_user(auth, username, password):
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/create"
    response = requests.post(
        url,
        auth=auth,
        json={
            "username": username,
            "password": password,
        },
    )
    if response.status_code == 200:
        print("New User addition successful")
    else:
        print("New User addition failed")

# Update a standard user as an admin
def update_user_as_admin(auth, username):
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/update-admin"
    response = requests.patch(
        url,
        auth=auth,
        json={
            "username": username,
            "is_admin": 0,
        },
    )
    if response.status_code == 200:
        print("User update successful")
    else:
        print("User update failed")

# Update the user(admin) password
def update_admin_password(auth, new_password):
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/update-password"
    response = requests.patch(
        url,
        auth=auth,
        json={
            "username": "user1",
            "password": new_password,
        },
    )
    if response.status_code == 200:
        print("Password update successful")
    else:
        print("Password update failed")

# Get user
def get_user(auth, username):
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/get"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    headers = {'Content-type': 'application/json'}
    params = {'username': username}
    response = requests.get(url, auth=auth, headers=headers, params=params)
    if response.status_code == 200:
        print("Get user object details successful")
        user_object = response.json().get('user', {})
        print(user_object )
        print(f"Experiment Permission (yes=[]): {user_object['experiment_permissions']}")
        print(f"Registered Model Permissions (yes, no): {user_object['registered_model_permissions']}")   
        print(f"Is admin (1, 0): {user_object['is_admin']}")     
    else:
        print("Get user object details failed")
    
    return user_object

# Delete a user
def delete_user(auth, username):
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/delete"
    response = requests.delete(
        url,
        auth=auth,
        json={
            "username": username
        },
    )
    if response.status_code == 200:
        print("User deletion successful")
    else:
        print("User deletion failed")

# Call the functions with the defined parameters
create_new_user(auth, new_user_username, new_user_password)
update_user_as_admin(auth, new_user_username)
update_admin_password(auth, user_password)
get_user(auth, new_user_username)
delete_user(auth, user_to_delete)


# curl -X POST "http://mlflow.dev.ai4eosc.eu/api/2.0/mlflow/users/get" \
#      -H "Content-Type: application/json" \
#      -u "admin:<password>" \
#      -d '{
#          "username": "user1"
#      }'