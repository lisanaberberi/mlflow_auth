# mlflow_auth



## Getting started

Implementing new feature of basic User Authentication in MLFlow.
There are the following python scripts that will serve admins to manage users and permission for specific resources: experiments and registered models.

```python
# Example script of an API cal:
#   url = f"{MLFLOW_REMOTE_SERVER}api/2.0/mlflow/users/create"
#    response = requests.post(
#       url,
#        auth=auth,
#        json={
#            "username": username,
#            "password": password,
#        },
#    ) ....


```
## Add your files
* [create_user.py](https://git.scc.kit.edu/m-team/ai/mlflow_auth/-/blob/main/create_user.py): 
Contains methods to create new users, update passwords, update standard users as admin and finally delete existing users are written
* [user_experiment_permission.py](https://git.scc.kit.edu/m-team/ai/mlflow_auth/-/blob/main/user_experiment_permission.py): Contain Methods to create new permissions to users for a given experiment, update existing experiment permission and delete them



## Authors and acknowledgment
This work is co-funded by AI4EOSC project that has received funding from the European Union's Horizon Europe 2022 research and innovation programme under agreement No 101058593

## License
For open source projects, say how it is licensed.
