from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from pkg_trainmote.databaseControllerModule import DatabaseController

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    users = DatabaseController().getUsers()
    print(users)
    for user in users:
        if username == user.username and check_password_hash(user.password, password):
            return user
    return None

@auth.get_user_roles
def get_user_roles(user):
    return user.roles
