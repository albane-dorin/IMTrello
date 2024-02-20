from userClass import *
from projectClass import *


class Trello:
    def __init__(self, users: list[User]):
        self.users = users

    def get_users(self):
        return self.users

    def create_account(self):

        users = getattr(self, "users")
        name = input("Enter your username: ")
        while True:
            password = input("Enter your password: ")
            confirm = input("Enter the same password: ")  #Check the password
            if password == confirm:
                break
            else:
                print("The two password aren't the same")
        while True:
            role = input("To be Developer enter 0, to be Manager enter 1, to be Both enter 2: ")
            match role:
                case "0":
                    users.append(Developer(name, password))
                    break
                case "1":
                    users.append(Manager(name, password))
                    break
                case "2":
                    users.append(ManDev(name, password))
                    break
                case _:
                    print("Invalid entry")

    def can_connect_user(self, name, password):
        exist = False
        for user in self.users:
            if user.name == name and user.password == password:
                exist = True
        return exist
