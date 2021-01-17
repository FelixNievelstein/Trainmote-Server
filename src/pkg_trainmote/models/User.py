from typing import Optional

class User():

    def __init__(
        self,
        uid: str,
        username: str,
        password: int,
        roles: Optional[str]
    ):
        self.uid = uid
        self.username = username
        self.password = password
        self.roles = roles

    def to_dict(self):
        return {
            "uid": self.uid,
            "username": self.username,
            "password": self.password,
            "roles": self.roles
        }