from userClass import *
from projectClass import *


class Trello:
    def __init__(self, users: list[User], projects: list[Project]):
        self.users = users
        self.projects = projects

    def get_users(self):
        return self.users

    def get_user_by_id(self, id):
        for user in self.users:
            if user.get_id() == id: return user

    def get_projects(self):
        return self.projects

    def get_project_by_id(self, id):
        for project in self.projects:
            if project.get_id() == id: return project

    def create_account(self, name, password, role):
        match role:
            case "0":
                self.users.append(Developer(name, password))
            case "1":
                self.users.append(Manager(name, password))
            case "2":
                self.users.append(ManDev(name, password))

    def can_get_user(self, name, password):
        exist = False
        for user in self.users:
            if user.name == name and user.password == password:
                exist = True
        return exist

    def add_project(self, project):
        self.projects.append(project)
