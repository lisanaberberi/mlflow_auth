
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
auth = HTTPBasicAuth("admin", "new_admin_password")

# Define the username and password for the new user
new_user_username = "mlflow_u"
new_user_password = "<password>"  #type a new password

# Define the new password of an existing user(admin)
user_password = "<password>" #type a new password

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
            "is_admin": 1,
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
            "username": "mlflow_u",
            "password": new_password,
        },
    )
    if response.status_code == 200:
        print("Password update successful")
    else:
        print("Password update failed")

# Call the functions with the defined parameters
create_new_user(auth, new_user_username, new_user_password)
update_user_as_admin(auth, new_user_username)
update_admin_password(auth, user_password)
