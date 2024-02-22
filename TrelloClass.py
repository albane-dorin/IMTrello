from userClass import *
from projectClass import *


class Trello:
    def __init__(self, users: list[User]):
        self.users = users

    def get_users(self):
        return self.users

    def create_account(self, name, password, role):
        users = getattr(self, "users")
        match role:
            case "0":
                users.append(Developer(name, password))
            case "1":
                users.append(Manager(name, password))
            case "2":
                users.append(ManDev(name, password))

    def can_connect_user(self, name, password):
        exist = False
        for user in self.users:
            if user.name == name and user.password == password:
                exist = True
        return exist
