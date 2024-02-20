from userClass import *

class Project():
    def __init__(self, id, name, description, time, manager):
        self.id = id
        self.name = name
        self.description = description
        self.time = time
        self.manager=manager

class Notification():
    def __init__(self, id, source, description):
        self.id = id
        self.source = source
        self.description = description

class Task():
    def __init__(self, id, titre, status, developers : list, endDate):
        self.id = id
        self.titre = titre
        self.status = status
        self.developers = developers
        self.endDate = endDate
