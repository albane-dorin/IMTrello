from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey



db = SQLAlchemy()


def init_database():
    db.create_all()


#Création des tables

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text)
    password = db.Column(db.Text)
    mail = db.Column(db.Text)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    manager = db.Column(db.Integer, ForeignKey('User.id'))

class Column(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    project = db.Column(db.Integer, ForeignKey('Project.id'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    column = db.Column(db.Integer, db.ForeignKey('Column.id'))

class Notif(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, db.ForeignKey('User.id'))
    content = db.Column(db.Text)

class Project_Task(db.Model):
    id_project = db.Column(db.Integer, ForeignKey('Project.id'), primary_key=True)
    id_task = db.Column(db.Integer, ForeignKey('Task.id'), primary_key=True)

class Project_Dvp(db.Model):
    id_project = db.Column(db.Integer, ForeignKey('Project.id'), primary_key=True)
    id_dvp = db.Column(db.Integer, ForeignKey('User.id') , primary_key=True)

class Task_Dvp(db.Model):
    id_task = db.Column(db.Integer, ForeignKey('Task.id') , primary_key=True)
    id_dvp = db.Column(db.Integer, ForeignKey('User.id') , primary_key=True)



#Peupler la base de donner pour les tests
def peupler_db():
    user1 = User(username="One", password="<PASSWORD>", mail="<EMAIL>")
    user2 = User(username="Two", password="<PASSWORD>", mail="<EMAIL>")
    db.session.add(user2)
    db.session.add(user1)

    project1 = Project(name="Project 1", description="Mon premier projet", date=datetime, manager=user1)
    project2 = Project(name="Project 2", description="Mon deuxième projet", date=datetime, manager=user1)
    db.session.add(project1)
    db.session.add(project2)

    c11 = Column(name='En cours', project=project1)
    c12 = Column(name='Fini =)', project=project1)
    c21 = Column(name='En avant toute !', project=project2)
    c22 = Column(name='Dernère ligne droite !', project=project2)
    db.session.add(c11)
    db.session.add(c12)
    db.session.add(c21)
    db.session.add(c22)

    task11 = Task(name="Task 1", description="Première tâche", date=datetime, column=c11)
    task12 = Task(name="Task 2", description="Deuxième tâche", date=datetime, column=c11)
    task13 = Task(name="Task 3", description="Troisième tâche", date=datetime, column=c12)
    task21 = Task(name="Tâche 1", description="Faire des trucs", date=datetime, column=c21)
    db.session.add(task11)
    db.session.add(task12)
    db.session.add(task13)
    db.session.add(task21)

    # Ajoutez les projets et les utilisateurs à des listes pour une utilisation ultérieure
    users = [user1, user2]
    projects = [project1, project2]

    # Ajoutez les tâches aux colonnes
    tasks = [task11, task12, task13, task21]

    # Pour Project_Task
    for project in projects:
        for task in tasks:
            # Ici, nous associons chaque tâche à chaque projet
            project_task = Project_Task(id_project=project.id, id_task=task.id)
            db.session.add(project_task)

    # Pour Project_Dvp
    for project in projects:
        for user in users:
            # Ici, nous associons chaque utilisateur à chaque projet
            project_dvp = Project_Dvp(id_project=project.id, id_dvp=user.id)
            db.session.add(project_dvp)

    # Pour Task_Dvp
    task_dvp = Task_Dvp(id_task=task11.id, id_dvp=user1.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task11.id, id_dvp=user2.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task12.id, id_dvp=user1.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task13.id, id_dvp=user1.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task13.id, id_dvp=user2.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task21.id, id_dvp=user1.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task21.id, id_dvp=user2.id)
    db.session.add(task_dvp)

    db.session.commit()
