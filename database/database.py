from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey


db = SQLAlchemy()


def init_database():
    db.create_all()


#Création des tables

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text)
    password = db.Column(db.Text)
    mail = db.Column(db.Text)
    role = db.Column(db.Integer) #1=Manager, 2=Développeur, 3=ManDev

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    manager = db.Column(db.Integer, ForeignKey('user.id'))

class Column(db.Model):
    __tablename__ = 'column'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    project = db.Column(db.Integer, ForeignKey('project.id'))

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    column = db.Column(db.Integer, db.ForeignKey('column.id'))
    status = db.Column(db.Integer)
    #WAITING = 0
    #IN_PROGRESS = 1
    #COMPLETED = 2
    #CANCELLED = 3
    #BLOCKED = 4

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)
    task = db.Column(db.Integer, ForeignKey('task.id'))

class Project_Task(db.Model):
    __tablename__ = 'project_task'
    id_project = db.Column(db.Integer, ForeignKey('project.id'), primary_key=True)
    id_task = db.Column(db.Integer, ForeignKey('task.id'), primary_key=True)

class Project_Dvp(db.Model):
    __tablename__ = 'project_dvp'
    id_project = db.Column(db.Integer, ForeignKey('project.id'), primary_key=True)
    id_dvp = db.Column(db.Integer, ForeignKey('user.id') , primary_key=True)

class Task_Dvp(db.Model):
    __tablename__ = 'task_dvp'
    id_task = db.Column(db.Integer, ForeignKey('task.id') , primary_key=True)
    id_dvp = db.Column(db.Integer, ForeignKey('user.id') , primary_key=True)

#Fonctions d'obtention d'informatio

#Est-ce que l'utilisateur est le manager du projet
def is_manager(user, project):
    if project.manager == user.id:
        return True
    else:
        return False

#Fonctions de modifications

#Ajout d'utilisateur
def new_user(username, password, mail, role):
    user = User(username=username, password=password, mail=mail, role=role)
    db.session.add(user)
    db.session.commit()

#Ajout de projet
def new_project(name, description, year, month, day, manager, users : list[User]):
    if manager.role == 2 :
        return
    project = Project(name=name, description=description, date=datetime(year, month, day), manager=manager.id)
    db.session.add(project)
    db.session.commit()
    for user in users:
        project_dvp = Project_Dvp(id_project=project.id, id_dvp=user.id)
        db.session.add(project_dvp)
    db.session.commit()

#Ajout de colonne
def new_column(name, project, user):
    if is_manager(user, project):
        column = Column(name=name, project=project.id)
        db.session.add(column)
        db.session.commit()
        return
    else:
        return

#Ajout tâche
def new_task(user, project, name, year, month, day, description, column, status, dvps):
    if is_manager(user, project):
        task = Task(name=name, date=datetime(year, month, day), description=description, column=column.id, status=status)
        db.session.add(task)
        db.session.commit()
        project_task = Project_Task(id_project=project.id, id_task=task.id)
        db.session.add(project_task)
        for dvp in dvps:
            dvp_task = Task_Dvp(id_task=task.id, id_dvp=dvp.id)
            db.session.add(dvp_task)
        db.session.commit()
        return
    else:
        return

#Ajout comment
def new_comment(author, task, content):
    comment = Comment(author=author.id, content=content, task=task.id)
    db.session.add(comment)
    db.session.commit()


    #effacer le contenu de la base de données
def clear_database():
    # Supprimer le contenu de chaque table
    db.session.query(User).delete()
    db.session.query(Project).delete()
    db.session.query(Column).delete()
    db.session.query(Task).delete()
    db.session.query(Comment).delete()
    db.session.query(Project_Task).delete()
    db.session.query(Project_Dvp).delete()
    db.session.query(Task_Dvp).delete()

    # Confirmer les changements et vider la base de données
    db.session.commit()

def clean():
    db.drop_all()
    db.create_all()
    return "Cleaned!"

#Peupler la base de donner pour les tests
def peupler_db():
    clean()

    user1 = User(username="One", password="<PASSWORD>", mail="<EMAIL>", role=1)
    user2 = User(username="Two", password="<PASSWORD>", mail="<EMAIL>", role=2)
    db.session.add(user2)
    db.session.add(user1)
    db.session.commit()

    project1 = Project(name="Project 1", description="Mon premier projet", date=datetime(2024, 3, 6), manager=user1.id)
    project2 = Project(name="Project 2", description="Mon deuxième projet", date=datetime(2024, 3, 6), manager=user1.id)
    db.session.add(project1)
    db.session.add(project2)
    db.session.commit()

    c11 = Column(name='En cours', project=project1.id)
    c12 = Column(name='Fini =)', project=project1.id)
    c21 = Column(name='En avant toute !', project=project2.id)
    c22 = Column(name='Dernère ligne droite !', project=project2.id)
    db.session.add(c11)
    db.session.add(c12)
    db.session.add(c21)
    db.session.add(c22)
    db.session.commit()

    task11 = Task(name="Task 1", description="Première tâche", date=datetime(2024, 3, 6), column=c11.id)
    task12 = Task(name="Task 2", description="Deuxième tâche", date=datetime(2024, 3, 6), column=c11.id)
    task13 = Task(name="Task 3", description="Troisième tâche", date=datetime(2024, 3, 6), column=c12.id)
    task21 = Task(name="Tâche 1", description="Faire des trucs", date=datetime(2024, 3, 6), column=c21.id)
    db.session.add(task11)
    db.session.add(task12)
    db.session.add(task13)
    db.session.add(task21)
    db.session.commit()

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
