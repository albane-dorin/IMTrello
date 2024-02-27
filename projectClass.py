import datetime

from userClass import *
from datetime import date
from enum import Enum


#############################################################
class Notification:

    def __init__(self, project_id, notif_type: str, task_id = None):
        self.project_id = project_id
        if task_id != None:
            self.task_id = task_id
        self.notif_type = notif_type

#############################################################
class Column:
    last_id = 0

    def __init__(self, name):
        self.name = name
        Column.last_id = Column.last_id + 1
        self.id = Column.last_id
        self.name = name

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def rename(self, new_name):
        self.name = new_name


# Méthodes

#############################################################
class Status(Enum):
    WAITING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    CANCELLED = 3
    BLOCKED = 4

#############################################################
class Comment:

    def __init__(self, author, name):
        self.author = author
        self.name = name

    def get_author(self):
        return self.author

    def get_name(self):
        return self.name

#############################################################
class Task:

    last_id = 0

# Constructors
    def __init__(self, name, description, idProject, column, developers: list[Developer], year, month, day):
        Task.last_id = Task.last_id + 1
        self.id = Task.last_id
        self.name = name
        self.description = description
        self.idProject = idProject
        self.column = column
        self.status = 0
        self.developers = developers
        self.endDate = datetime.date(year, month, day)
        self.comments = []
        for dvp in developers:
            dvp.addNotif(Notification(self.idProject, "Nouvelle tâche", self.id))

    # Getter
    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_idProject(self):
        return self.idProject

    def get_column(self):
        return self.column

    def get_status(self):
        return self.status

    def get_developers(self):
        return self.developers

    def get_endDate(self):
        return self.endDate

    def get_comments(self):
        return self.comments

# Methods
    def rename(self, new_name):
        self.name = new_name

    def new_description(self, new_description):
        self.description = new_description

    def move_column(self, new_column : Column) :
        self.column = new_column

    def new_status(self, new_status : Status):
        self.status = new_status

    def add_developer(self, new_developer):
        self.developers.append(new_developer)
        new_developer.addNotif(Notification(self.idProject, "Nouvelle tâche", self.get_id()))

    def remove_developer(self, new_developer):
        self.developers.remove(new_developer)

    def new_endDate(self, year, month, day):
        self.endDate = datetime.date(year, month, day)
        for dvp in self.get_developers() :
            dvp.addNotif(Notification(self.idProject, "Attention. Nouvelle date.", self.get_id()))

    def add_comments(self, new_comments : Comment):
        self.comments.append(new_comments)
        for dvp in self.get_developers():
            dvp.addNotif(Notification(self.idProject, "Nouveau commentaire", self.get_id()))

    #Check if the end date is near (less than 3 days)
    def is_soon(self):
        if self.endDate - datetime.timedelta(days=3) < datetime.date.today() <= self.endDate:
            return True
        else:
            return False

    def is_late(self):
        if self.endDate<datetime.datetime.now().date():
            return True
        else:
            return False

#############################################################

class Project:
    last_id = 0

    # Constructors
    def __init__(self, name, description, year, month, day, columns: list[Column], manager: Manager,
                 workers: list[Developer]):
        # Characteristics
        Project.last_id = Project.last_id + 1
        self.id = Project.last_id
        self.name = name
        self.description = description
        self.end_date = datetime.date(year, month, day)
        # Contenu
        self.columns = columns
        self.tasks = []
        # Utilisateurs
        self.manager = manager
        self.workers = workers
        for worker in workers:
            worker.addNotif(self.get_id(), "Nouveau projet")

    # Getter
    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_time(self):
        return self.time

    def get_columns(self):
        return self.columns

    def get_tasks(self):
        return self.tasks

    def get_manager(self):
        return self.manager

    def get_workers(self):
        return self.workers

    # Méthodes

    # Change the title of the project. new_name is a string
    def rename(self, new_name):
        self.name = new_name

    # Change the description of the project. new_description is a string
    def new_description(self, new_description):
        self.description = new_description

    # Add a new column. column is a Column
    def new_column(self, column):
        self.columns.append(column)

    # delete a column. column is a Column
    def delete_column(self, column):
        self.columns.remove(column)

    # add a new task. new_task is a task
    def new_task(self, task:Task):
        self.tasks.append(task)

    # delete task. task is a Task
    def delete_task(self, task):
        self.tasks.remove(task)

    # Add a developer. worker is a Developer
    def add_worker(self, worker):
        self.workers.append(worker)
        worker.addNotif(self.get_id(),"Nouveau Projet")

    # Delete a worker. worker in a Developer
    def delete_worker(self, worker):
        self.workers.remove(worker)