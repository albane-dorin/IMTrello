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

class Notif(db.Model):
    __tablename__ = 'notif'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)
    link_task = db.Column(db.Integer, db.ForeignKey('task.id'))
    link_project = db.Column(db.Integer, db.ForeignKey('project.id'))

#Fonctions d'obtention d'informatio

#Est-ce que l'utilisateur est le manager du projet ?
def is_manager(user, project):
    if project.manager == user.id:
        return True
    else:
        return False

#Quel est le projet auquel appartient cette tâche
def id_project_of(task):
    id_task = task.id
    project_task = Project_Task.query.filter_by(id_task=id_task).first()
    if project_task:
        return project_task.id_project
    else:
        return None

def project_of(task):
    project_id = id_project_of(task)
    project = Project.query.get(project_id)
    return project

def projects_of_user(user):
    id=user.id
    ps_dvp=Project_Dvp.query.filter_by(id_dvp=id).all()
    projects = []
    for x in ps_dvp:
        idx= x.id_project
        projects.append(Project.query.get(idx))
    return projects

def tasks_of_user(user):
    id=user.id
    ts_dvp=Task_Dvp.query.filter_by(id_dvp=id).all()
    tasks = []
    for x in ts_dvp:
        idx= x.id_task
        tasks.append(Task.query.get(idx))
    return tasks


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
    p_id=project.id
    for user in users:
        project_dvp = Project_Dvp(id_project=p_id, id_dvp=user.id)
        db.session.add(project_dvp)
        notif = Notif(user=user.id,content="Une nouvelle aventure vous attend, vous avez rejoit le projet "+name,
                      link_project=p_id)
        db.session.add(notif)
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
        db.session.commit()
        t_id = task.id
        p_id=id_project_of(task)
        for dvp in dvps:
            dvp_task = Task_Dvp(id_task=t_id, id_dvp=dvp.id)
            db.session.add(dvp_task)
            notif = Notif(user=dvp.id, link_task=t_id, link_project=p_id,
                          content="Une nouvelle mission ! Vous avez été ajouté à la tâche "+name)
            db.session.add(notif)
            db.session.commit()
        return
    else:
        return

#Ajout comment
def new_comment(author, task, content):
    comment = Comment(author=author.id, content=content, task=task.id)
    db.session.add(comment)
    db.session.commit()


#Ajout de développeurs à un projet/tâche
def add_dvp_to_project(user, project, dvp):
    if is_manager(user, project):
        dvp_project = Project_Dvp(id_project=project.id, id_dvp=dvp.id)
        db.session.add(dvp_project)
        notif = Notif(user=dvp.id, link_project=project.id, content="Une nouvelle aventure vous attend, vous avez rejoit le projet "+project.name)
        db.session.commit()

def add_dvp_to_task(user, task, dvp):
    id = id_project_of(task)
    dvp_in_project = Project_Dvp.query.filter_by(id_project=id).all()
    dvps = []
    for d in dvp_in_project:
        dvps.append(d.id_dvp)
    for i in range(0, len(dvps)):
        if dvp.id==dvps[i]:
            td = Task_Dvp(id_task=task.id, id_dvp=dvp.id)
            db.session.add(td)
            notif = Notif(user=dvp.id, link_task=task.id, link_project=id,
                          content="Une nouvelle mission ! Vous avez été ajouté à la tâche " + task.name)
            db.session.add(notif)
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

    user1 = User(username="Lovely", password="coeur", mail="lovely@gmail", role=3)
    user2 = User(username="Two", password="<PASSWORD>", mail="<EMAIL>", role=2)
    db.session.add(user2)
    db.session.add(user1)
    db.session.commit()

    project1 = Project(name="Project 1", description="Mon premier projet", date=datetime(2024, 3, 13), manager=user1.id)
    project2 = Project(name="Project 2", description="Mon deuxième projet", date=datetime(2024, 4, 6), manager=user1.id)
    project3 = Project(name="Website", description="Design du page d'acceuil pour afficher les informations de l'entreprise en temps réel", date=datetime(2024, 6, 6), manager=user1.id)
    db.session.add(project1)
    db.session.add(project2)
    db.session.add(project3)
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

    task11 = Task(name="Task 1", description="Première tâche", date=datetime(2024, 3, 11), column=c11.id)
    task12 = Task(name="Task 2", description="Deuxième tâche", date=datetime(2024, 3, 13), column=c11.id)
    task13 = Task(name="Task 3", description="Troisième tâche", date=datetime(2024, 3, 17), column=c12.id)
    task21 = Task(name="Tâche 1", description="Faire des trucs", date=datetime(2024, 4, 4), column=c21.id)
    task31 = Task(name="Cdc", description="Etablir et valider le cahier des charges pour l'entreprise", date=datetime(2024,3,9))
    task32 = Task(name="Maquette", description="Réaliser la maquette et la valider auprès du client", date=datetime(2024,3,19))
    task33 = Task(name="Front-end", description="Etablir et valider le cahier des charges pour l'entreprise", date=datetime(2024,4,20))
    task34 = Task(name="Integration API", description="Etablir et valider le cahier des charges pour l'entreprise", date=datetime(2024,5,20))
    task35 = Task(name="Integration Calendar", description="Etablir et valider le cahier des charges pour l'entreprise", date=datetime(2024,5,30), status="1")

    db.session.add(task11)
    db.session.add(task12)
    db.session.add(task13)
    db.session.add(task21)
    db.session.add(task31)
    db.session.add(task32)
    db.session.add(task33)
    db.session.add(task34)
    db.session.add(task35)
    db.session.commit()

    # Ajoutez les projets et les utilisateurs à des listes pour une utilisation ultérieure
    users = [user1, user2]
    projects = [project1, project2,project3]

    # Ajoutez les tâches aux colonnes
    tasks = [task11, task12, task13, task21, task31, task32, task33, task34, task35]

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
    task_dvp = Task_Dvp(id_task=task31.id, id_dvp=user1.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task32.id, id_dvp=user1.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task33.id, id_dvp=user1.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task34.id, id_dvp=user1.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task35.id, id_dvp=user1.id)
    db.session.add(task_dvp)

    #Notifs
    n1 = Notif(user=2, content="J'ai une notif")
    n2 = Notif(user=2, content="Vous avez rejoint le projet 'Hello'", link_project=1)
    n3 = Notif(user=2, content="L'échéance de la tâche HelloWorld arrive bientôt", link_task=2)
    db.session.add(n1)
    db.session.add(n2)
    db.session.add(n3)


    db.session.commit()
