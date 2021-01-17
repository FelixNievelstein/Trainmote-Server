from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from pkg_trainmote.databaseControllerModule import DatabaseController

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    users = DatabaseController().getUsers()
    print(next(u for u in users if u.username == username and check_password_hash(u.password, password)))
    return next(u for u in users if u.username == username and check_password_hash(u.password, password))

@auth.get_user_roles
def get_user_roles(user):
    print(user)
    return user.roles
