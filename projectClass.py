import datetime

from userClass import *
from datetime import date
from enum import Enum


class Project:
    last_id = 0

    # Constructors
    def __init__(self, name, description, year, month, day, columns: list[Column], tasks: list[Task], manager: Manager,
                 workers: list[Developer]):
        # Characteristics
        Project.last_id = Project.last_id + 1
        self.id = Project.last_id
        self.name = name
        self.description = description
        self.end_date = datetime.date(year, month, day)
        # Contenu
        self.columns = columns
        self.tasks = tasks
        # Utilisateurs
        self.manager = manager
        self.workers = workers

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
    def new_task(self, task):
        self.tasks.append(task)

    # delete task. task is a Task
    def delete_task(self, task):
        self.tasks.remove(task)

    # Add a developer. worker is a Developer
    def add_worker(self, worker):
        self.workers.append()

    # Delete a worker. worker in a Developer
    def delete_worker(self, worker):
        self.workers.remove(worker)


###############################################################
class Notification:
    last_id = 0

    def __init__(self, id, source, description):
        Notification.last_id = Notification.last_id + 1
        self.id = Notification.last_id
        self.source = source
        self.description = description


##########################################
class Column():
    last_id = 0

    def __init__(self, id, name):
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


#######################################################""""
class Status(Enum):
    WAITING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    CANCELLED = 3
    BLOCKED = 4



#########################################################
class Task:
    last_id = 0

# Constructors
    def __init__(self, titre, description, column, developers: list[Developer], year, month, day):
        Task.last_id = Task.last_id + 1
        self.id = Task.last_id
        self.titre = titre
        self.description = description
        self.column = column
        self.status = 0
        self.developers = developers
        self.endDate = datetime.date(year, month, day)
        self.comments = None

    # Getter
    def get_id(self):
        return self.id

    def get_titre(self):
        return self.titre

    def get_description(self):
        return self.description

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

    def remove_developer(self, new_developer):
        self.developers.remove(new_developer)

    def new_endDate(self, new_endDate):
        self.endDate = new_endDate

    def add_comments(self, new_comments):
        self.comments.append(new_comments)

    #Check if the end date is near (less than 3 days)
    def  is_soon(self):
        if datetime.date.today()-3 < self.endDate < datetime.date.today():
            return True
        else :
            return False

    def is_late(self):
        if self.endDate>datetime.date.today():
            return True
        else:
            return False