
import mlflow
from mlflow.tracking.client import MlflowClient

import requests
from requests.auth import HTTPBasicAuth
import getpass

import subprocess # to exe cmd line commands
import pyfiglet

# Remote MLFlow server
MLFLOW_REMOTE_SERVER="http://mlflow.dev.ai4eosc.eu/"

#initialize an instance to request and query the MLflow server.
client = MlflowClient()

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

#This function only results with one experiment result for all users, the "Default" exp
# def list_all_exp():
#     # Define the command
#     command = "mlflow experiments search --view all"

#     # Execute the command
#     result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

#     # Check the result
#     if result.returncode == 0:
#         # Command was successful
#         print("Command executed successfully.")
#         print("Output:")
#         print(result.stdout)
        
#         # Parse the output to extract experiment names
#         experiment_names = []
#         lines = result.stdout.split('\n')
#         for line in lines:
#             # Experiment names are in the second column
#             columns = line.split()
#             if len(columns) >= 2:
#                 experiment_names.append(columns[1])

#         return experiment_names

#     else:
#         # Command encountered an error
#         print("Command failed with the following error:")
#         print(result.stderr)
#         return []

def search_exps(experiment_name):
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/experiments/search"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    headers = {'Content-type': 'application/json'}

    # Define search parameters
    search_params = {
        'filter': f"name LIKE '%{experiment_name}%'",
        'max_results': 100,  # Set the desired max results
        'order_by': ["name ASC"],  # Order by experiment name in ascending order
        'view_type': "ALL"  # You can change this to your desired view type
    }

    response = requests.get(url, auth=auth, headers=headers, params=search_params)

    if response.status_code == 200:
        data = response.json()
        experiments = data.get('experiments', [])
        for experiment in experiments:
            print("\n" + GREEN + f"Experiment Name: {experiment['name']}" + RESET)
            print("\n" + GREEN + f"Experiment ID: {experiment['experiment_id']}" + RESET)
            print("\n" + GREEN + f"Artifact Location: {experiment['artifact_location']}" + RESET)
    else:
        print("\n" + RED + f"Failed to retrieve experiments details. Status code: {response.status_code}" + RESET)

   

# Function to authenticate as admin
def authenticate_as_admin():
    global auth
    global MLFLOW_TRACKING_USERNAME
    global MLFLOW_TRACKING_PASSWORD

    MLFLOW_TRACKING_USERNAME = input("Enter your username: ")
    MLFLOW_TRACKING_PASSWORD = getpass.getpass("Enter your password: ")
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)

    if is_admin_authenticated() == 200:
        print("\n" + GREEN + "Authentication successful." + RESET)
        display_menu()
    else:
        print("\n" + RED + "Authentication failed." + RESET)

def is_admin_authenticated():
    # Check if admin authentication is successful
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/get"
    headers = {'Content-type': 'application/json'}
    params = {'username': MLFLOW_TRACKING_USERNAME}
    response = requests.get(url, auth=auth, headers=headers, params=params)
    return response.status_code

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

def create_exp_permission(experiment_name, username, permission):
    # Specify the experiment name you want to grant to the user
    experiment = get_experiment_details(experiment_name)
    if experiment is not None:
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
            print("\n" + GREEN + f"Experiment permissions created for the given user. Status code: {response.status_code}" + RESET)
        elif response.status_code == 400:
            print("\n" + RED + f"Resource already exists and only one permission can be assigned to a user for a given exp. Status code: {response.status_code}" + RESET)
        else:
            print("\n" + RED + f"Experiment permission with experiment_id= {experiment_id} and username= {username} not found. Status code: {response.status_code}" + RESET)      
        return experiment_id, username, permission
    else:
        print("\n" + RED + "Experiment does not exist!" + RESET)


# GET EXP permissions, you need an experiment_id (needs to be found based on the name) and username
def get_exp_permission(experiment_name, username):
    
    experiment = get_experiment_details(experiment_name)
    if experiment != None:
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
        #exp_user_perm = response.json()
        print("\n" + GREEN + f"Experiment permission update successful. Status code: {response.status_code}" + RESET)
    else:
        print("\n" + RED + f"Experiment permission with experiment_id= {experiment_id} and username= {username} not found. Status code: {response.status_code}" + RESET)



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
        print("\n" + GREEN + f"Experiment permission delete successful. Status code: {response.status_code}"+ RESET) 
    else:
        print("\n" + RED + f"Experiment permission delete failed. Status code: {response.status_code}" + RESET)


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
                print("\n" + GREEN + f"No runs found for the specified experiment. Status code: {response.status_code}" + RESET)
        else:
            print("\n" + RED + f"Failed to retrieve runs details. Status code: {response.status_code}" + RESET)       
    else:
        print("\n" + RED + "No experiment details found. Status code" + RESET)

    return experiment_id, runs

# Function to select and show details of a specific run
def select_and_show_run_details(experiment_name, runs):
    if not runs:
        print("No runs available for selection.")
        return

    selected_run_index = int(input("Select a run (enter the number, not the ID): ")) - 1
    if 0 <= selected_run_index < len(runs):
        selected_run = runs[selected_run_index]
        run_uuid = selected_run['info']['run_id']
        print(f"Selected Run ID: {run_uuid}")

        # Show details of the selected run
        print("Run Details:")
        print(f"Experiment Name: {experiment_name}")
        print(f"Run UUID: {run_uuid}")
    else:
        print("Invalid selection. Please enter a valid run number.")

    # Usage for getting run details
    experiment_id, runs = get_runs_details_of_exp(experiment_name)
    # Usage for selecting and showing run details
    if experiment_id is not None:
        select_and_show_run_details(experiment_name, runs)


#####------- Model-user permissions management as follow-------######

#1. first 
def search_model_client_auth():
#first make sure you have setup the environment vars to authenticate to the server
    for rm in client.search_registered_models():
        print(dict(rm), indent=4)


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
        print("\n" + GREEN + f"Next page token: {response.json().get('next_page_token')}" + RESET)
    else:
        print("\n" + RED + f"Failed to retrieve experiments details. Status code: {response.status_code}" + RESET)

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
        print("\n" + RED + f"Failed to retrieve model details. Status code: {response.status_code}" + RESET)

    return registered_model

# Make an API request to get model's permission object details
def get_model_permission_details(model_name, username):
    
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/registered-models/permissions/get"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    headers = {'Content-type': 'application/json'}
    params = {'name': model_name,
            'username': username}
    response = requests.get(url, auth=auth, headers=headers, params=params)

    if response.status_code == 200:
        response_json = response.json()
        registered_model_perm = response_json.get('registered_model_permission', {})
        
        if isinstance(registered_model_perm, dict):
            print("\n" + GREEN + f"Model name: {registered_model_perm.get('name')}" + RESET)
            print("\n" + GREEN + f"Permissions: {registered_model_perm.get('permission')}" + RESET)
            print("\n" + GREEN + f"User-id: {registered_model_perm.get('user_id')}" + RESET)
        else:
            print("\n" + RED + "Registered model permission is not a dictionary." + RESET)
    else:
        print("\n" + RED + f"Failed to retrieve model permission details. Status code: {response.status_code}" + RESET)


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
        print("\n" + GREEN + f"Permission= {permission} has been given to user={username} for the registered model={model_name}." 
                 f"Status code: {response.status_code}"+ RESET)
    elif response.status_code == 400:
        print("\n" + RED + f"Resource already exists and only one permission can be assigned to a user for a given model."
              f"Status code: {response.status_code}" + RESET)
    else:
        print("\n" + RED + f"Registered Model permission of model_name= {model_name} and username= {username} not found."
              f"Status code: {response.status_code}"+ RESET)      

    return model_name, username, permission

# UPDATE model permissions, you need a model name, username and passw

def udpate_regModel_permission(model_name, username, permission):
    
   # experiment = get_experiment_details(model_name)

    #first check what are the current exp permissions to the given user
    get_model_details(model_name)
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/registered-models/permissions/update"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    response = requests.patch(
    url,
    auth=auth,
    json={
        "name": model_name,
        "username": username,
        "permission": permission
    },
    )       
    if response.status_code == 200:
        exp_user_perm = response.json()
        print("\n" + RED + f"Model permission update successful. Status code: {response.status_code}" + RESET)
        return exp_user_perm
    else:
        print("\n" + RED + f"Model permission with model-name= {model_name} and username= {username} not found. Status code: {response.status_code}" + RESET)

    

def delete_regModel_permission(model_name, username):
    
    model_name = get_model_details(model_name)
 
    url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/registered-models/permissions/delete"
    auth = HTTPBasicAuth(MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD)
    response = requests.delete(
    url,
    auth=auth,
    json={
        "name": model_name,
        "username": username
    },
    )       
    if response.status_code == 200:
        print("\n" + RED + f"Model permission delete successful. Status code: {response.status_code}" + RESET)
    else:
        print("\n" + RED + f"Model permission delete failed. Status code: {response.status_code}" + RESET)

def display_menu():
    while True:
        print("Menu:")
        print("0. List all the experiments granted to you")
        print("1. Add Experiment-User Permission")
        print("2. Get Experiment-User Permission")
        print("3. Update Experiment-User Permission")
        print("4. Delete Experiment-User Permission")
        print("5. List Runs for an Experiment")
        print("6. Add RegisteredModel-User Permission")
        print("7. Get RegisteredModel-User Permission")
        print("8. Update RegisteredModel-User Permission")
        print("9. Delete RegisteredModel-User Permission")
        print("10. List RegisteredModel")
        print("11. Exit")

        choice = input("Enter your choice (0/1/2/3/4/5/6/7/8/9/10/11): ")

        if choice == "0":
            experiment_name = input("Enter a possible experiment-name: ")
            search_exps(experiment_name)
        elif choice == "1":
            experiment_name = input("Enter the experiment name: ")
            username = input(f"Enter the username you want to grant permissions to experiment: :{experiment_name}_________")
            permission = input(f"Enter the permission for the user: <:{username}> (i.e. READ or EDIT, MANAGE, No_Permission):____")
            create_exp_permission(experiment_name, username, permission)
        elif choice == "2":
            experiment_name = input("Enter the experiment name: ")
            #experiment_names = list_all_exp()
            #for exp in experiment_names:
                #if exp == experiment_name:
            get_experiment_details(experiment_name)
            username = input("Enter the username you want to show what permissions (s)he have for the experiment: ")
            get_exp_permission(experiment_name, username)
        elif choice == "3":
            experiment_name = input("Enter the experiment name you want to update its permissions: ")
            username = input("Enter the username: ")
            permission = input("Enter the new permission for the user/experiment: ")
            udpate_exp_permission(experiment_name, username, permission)
        elif choice == "4":
            experiment_name = input("Enter the experiment name which you want to revoke permissions: ")
            username = input("Enter the username you want to revoke his/her permissions: ")
            delete_exp_permission(experiment_name, username)
        elif choice == "5":
            experiment_name = input("Enter the experiment name: ")
            experiment_id, runs = get_runs_details_of_exp(experiment_name)
        elif choice == "6":
            model_name = input("Enter the Registered Model name: ")
            username = input(f"Enter the username you want to grant permissions to the model: :{model_name}")
            permission = input("Enter the permission: ")
            create_regModel_permission(model_name, username, permission)
        elif choice == "7":
            model_name = input("Enter the Registered Model name: ")
            username = input("Enter the username you want to show what permissions (s)he have for the model: ")
            get_model_permission_details(model_name, username)
        elif choice == "8":
            model_name = input("Enter the model name you want to update its permissions: ")
            username = input("Enter the username: ")
            permission = input("Enter the new permission for the user/experiment: ")
            udpate_regModel_permission(model_name, username, permission)
        elif choice == "9":
            model_name = input("Enter the model name: ")
            username = input("Enter the username you want to revoke grant privileges: ")
            delete_regModel_permission(model_name, username)
        elif choice == "10":
            print("\n---------------------------------------\n")
            search_model_API()            
        elif choice == "11":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    word=pyfiglet.figlet_format("MLFlow User Permissions")
    print (word + "\n")
    while True:
        if authenticate_as_admin():
            break  # Exit the loop if authentication is successful
        else:
            print("User authentication failed")
            response = input("Do you want to try with a different username/password? (yes/no): ")
            if response.lower() != "yes":
                break  # Exit the loop if the user doesn't want to retry
