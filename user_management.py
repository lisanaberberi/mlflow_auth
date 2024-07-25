
import mlflow
from mlflow.tracking.client import MlflowClient

import requests
from requests.auth import HTTPBasicAuth
import getpass

import pyfiglet

# Remote MLFlow server
MLFLOW_REMOTE_SERVER="https://mlflow.dev.ai4eosc.eu/"


#Set the MLflow server and backend and artifact stores
mlflow.set_tracking_uri(MLFLOW_REMOTE_SERVER)

#customize some printing messages colors
RED = "\033[91m"    # Red
RESET = "\033[0m"   # Reset color
GREEN = "\033[92m"  # Green


# Define your authentication credentials
auth = None
MLFLOW_TRACKING_USERNAME = None
MLFLOW_TRACKING_USERNAME = None

# Function to authenticate as admin
def authenticate_as_admin():
    global auth
    global MLFLOW_TRACKING_USERNAME
    global MLFLOW_TRACKING_PASSWORD

    MLFLOW_TRACKING_USERNAME = input("Enter the **admin** username: ")
    MLFLOW_TRACKING_PASSWORD = getpass.getpass("Enter the admin password: ")
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)

    if is_admin_authenticated() == 200:
        print("\n" + GREEN + "Authentication successful. You are an admin." + RESET)
        show_menu()
    else:
        print("\n" + RED + "Authentication failed. You are not an admin." + RESET)

def is_admin_authenticated():
    # Check if admin authentication is successful
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/get"
    headers = {'Content-type': 'application/json'}
    params = {'username': MLFLOW_TRACKING_USERNAME}
    response = requests.get(url, auth=auth, headers=headers, params=params)
    return response.status_code


 #Create a new user
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
        print("\n" + GREEN + "New User addition successful" + RESET) 
    else:
        print("\n" + RED + "New User addition failed(user already exists!!!)" + RESET)

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
        print("\n" + GREEN + " User update successful" + RESET) 
    else:

        print("\n" + RED + "User update failed" + RESET)

# Update the user(admin) password
def update_password(auth, username, password):
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/update-password"
    response = requests.patch(
        url,
        auth=auth,
        json={
            "username": username,
            "password": password,
        },
    )
    if response.status_code == 200:
        print("\n" + GREEN + "Password update successful" + RESET)
    else:
        print("\n" + RED + "Password update failed" + RESET)

# Get user
def get_user(auth, username):
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/get"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    headers = {'Content-type': 'application/json'}
    params = {'username': username}
    response = requests.get(url, auth=auth, headers=headers, params=params)
    user_object=None
    if response.status_code == 200:
        print("Get user object details successful")
        user_object = response.json().get('user', {})
        print(user_object )
        print(f"Experiment Permission (yes=[]): {user_object['experiment_permissions']}")
        print(f"Registered Model Permissions (yes, no): {user_object['registered_model_permissions']}")   
        print(f"Is admin (1, 0): {user_object['is_admin']}")     
    else:
        print("\n" + RED + "Get user object details failed" + RESET)
    
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
        print("\n" + GREEN + "User deletion successful" + RESET)
    else:
        print("\n" + RED + "User deletion failed" + RESET)

# Function to show the menu
def show_menu():
    while True:
        print("\nMenu:")
        print("1. 🌟 Create User")
        print("2. 🛠️ Update User as Admin")
        print("3. 🔑 Update Admin Password")
        print("4. 🧐 Get User")
        print("5. 🗑️ Delete User")
        print("6. ❌ Exit")

        choice = input("\nEnter your choice (1/2/3/4/5/6): ")

        if choice == "1":
            username=input("\nEnter the new username: ")
            password=getpass.getpass("Enter the password for the user: ")
            create_new_user(auth, username, password)
        elif choice == "2":
            username=input("\nEnter the user to add as admin: ")
            update_user_as_admin(auth, username)
        elif choice == "3":
            password=getpass.getpass("\nEnter the new password: ")
            username=MLFLOW_TRACKING_USERNAME
            update_password(auth, username, password)
        elif choice == "4":
            username=input("\nEnter the username you want to get info for: ")
            get_user(auth, username)
        elif choice == "5":
            username=input("\nEnter the username you want to delete: ")
            delete_user(auth, username)
        elif choice == "6":
            print("\nExiting the program.")
            break
        else:
            print("\nInvalid choice. Please select a valid option.")

if __name__ == "__main__":
    word=pyfiglet.figlet_format("MLFlow User Management")
    print (word + "\n")
    while True:
        if authenticate_as_admin():
            break  # Exit the loop if authentication is successful
        else:
            print("User authentication failed")
            response = input("Do you want to try with a different username/password? (yes/no): ")
            if response.lower() != "yes":
                break  # Exit the loop if the user doesn't want to retry