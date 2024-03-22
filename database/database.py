from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy import join


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
    date = db.Column(db.Date)
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
    date = db.Column(db.Date)
    description = db.Column(db.Text)
    column = db.Column(db.Integer, db.ForeignKey('column.id'))
    status = db.Column(db.String)
    # Définir une contrainte de vérification pour l'attribut
    __table_args__ = (
        CheckConstraint(status.in_(['En attente', 'En cours', 'Completée','Annulée', 'En pause'])),
    )
    #WAITING = 0
    #IN_PROGRESS = 1
    #COMPLETED = 2
    #CANCELLED = 3
    #BLOCKED = 4
    priority = db.Column(db.String)
    __table_args__ = (
        CheckConstraint(priority.in_(['Facultative', 'Faible', 'Moyenne', 'Forte', 'Importante'])),
    )

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


def get_projects_tasks(user_id):
    # Effectuer la jointure entre Project et Project_Task
    project_and_id_tasks = join(Project, Project_Task, Project.id.label('id_project') == Project_Task.id_project)
    # return project_and_id_tasks
    # Effectuer la jointure entre Project_Task et Task
    query = (db.session.query(
        Project_Task,
        Project.id.label('p_id'),
        Project.name.label('p_name'),
        Project.manager,
        Task.id.label('t_id'),
        Task.name.label('t_name'),
        Task.date,
        Task.status,
        Task.priority.label('t_prio'),
        User.username.label('m_name')
    ).join(
        Project, Project.id == Project_Task.id_project
    ).join(
        Task, Task.id == Project_Task.id_task
    ).join(
        User, Project.manager == User.id
    ).filter(
        Project.manager == user_id
    ).all())
    #result=query.subquery()
    return query

def get_dvps_of_project(project_id):
    project_dvps = Project_Dvp.query.filter_by(id_project=project_id).all()
    list = []
    for project_dvp in project_dvps:
        id = project_dvp.id_dvp
        dvp = db.session.get(User, id)
        list.append(dvp)
    return(list)

def get_dvps_of_task(task_id):
    task_dvps = Task_Dvp.query.filter_by(id_task=task_id).all()
    list=[]
    for task_dvp in task_dvps:
        id = task_dvp.id_dvp
        dvp = db.session.get(User, id)
        list.append(dvp)
    return(list)

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

def delete_project(project_id, user):
    print(is_manager(user, db.session.get(Project, project_id)))
    if is_manager(user, db.session.get(Project, project_id)):
        project = db.session.get(Project, project_id)
        #Développer
        dvp_ps = db.session.query(Project_Dvp).filter_by(id_project=project.id)
        for dvp_p in dvp_ps :
            db.session.delete(dvp_p)
        #Tâches
        task_ps=db.session.query(Project_Task).filter_by(id_project=project.id)
        for task_p in task_ps:
            id_task = task_p.id_task
            task_dvps = db.session.query(Task_Dvp).filter_by(id_task=id_task).all()
            for task_dvp in task_dvps:
                db.session.delete(task_dvp)
            db.session.delete(task_p)
            comments = db.session.query(Comment).filter_by(task=id_task).all()
            for comment in comments:
                db.session.delete(comment)
            task= db.session.get(Task, id_task)
            db.session.delete(task)
        #colonnes
        cs=db.session.query(Column).filter_by(project=project.id).all()
        for column in cs:
            db.session.delete(column)
        #projet
        db.session.delete(project)
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
def new_task(user, project, name, year, month, day, description, column, status, priority, dvps):
    if is_manager(user, project):
        task = Task(name=name, date=datetime(year, month, day), description=description, column=column.id, status=status, priority=priority)
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

def delete_task(task, user, project):
    if is_manager(user, project):
        t_dvps=db.session.query(Task_Dvp).filter_by(id_task=task.id).all()
        for t_dvp in t_dvps:
            db.session.delete(t_dvp)
        t_ps = db.session.query(Project_Task).filter_by(id_task=task.id).all()
        for t_p in t_ps:
            db.session.delete(t_p)
        comments = db.session.query(Comment).filter_by(task=task.id).all()
        for comment in comments:
            db.session.delete(comment)
        db.session.delete(task)
        db.session.commit()


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
        db.session.commit()

def delete_dvp_of_project(user, project, dvp):
    if is_manager(user, project):
        #Supprime dvp de project
        dvps_projects = db.session.query(Project_Dvp).filter_by(id_project=project.id).filter_by(id_dvp=dvp.id).all()
        for dvp_p in dvps_projects:
            db.session.delete(dvp_p)
        #Supprime dvp de ses différentes tâches
        dvps_tasks = db.session.query(Task_Dvp).filter_by(id_dvp=dvp.id).all()
        for dvp_t in dvps_tasks:
            db.session.delete(dvp_t)
        db.session.commit()

def add_dvp_to_task(user, task, dvp):
    if is_manager(user, project_of(task)):
        id = id_project_of(task)
        dvp_in_project = Project_Dvp.query.filter_by(id_project=id).all()
        dvps = []
        for d in dvp_in_project:
            dvps.append(d.id_dvp)
        for i in range(0, len(dvps)):
            if dvp.id==dvps[i]:
                td = Task_Dvp(id_task=task.id, id_dvp=dvp.id)
                db.session.add(td)
                db.session.commit()

def delete_dvp_of_task(user, task, dvp):
    if is_manager(user, project_of(task)):
        task_dvps=db.session.query(Task_Dvp).filter_by(id_task=task.id).filter_by(id_dvp=dvp.id).all()
        for t in task_dvps:
            db.session.delete(t)
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

    task11 = Task(name="Task 1", description="Première tâche", date=datetime(2024, 3, 6), column=c11.id, status = 'En attente', priority='Facultative')
    task12 = Task(name="Task 2", description="Deuxième tâche", date=datetime(2023, 3, 6), column=c11.id, status = 'Annulée', priority='Moyenne')
    task13 = Task(name="Task 3", description="Troisième tâche", date=datetime(2024, 4, 6), column=c12.id, status = 'En pause', priority='Faible')
    task21 = Task(name="Tâche 1", description="Faire des trucs", date=datetime(2024, 3, 7), column=c21.id, status = 'En cours', priority='Forte')
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
    for task in tasks[:2+1]:
        # Ici, nous associons chaque tâche à chaque projet
        project_task = Project_Task(id_project=projects[0].id, id_task=task.id)
        db.session.add(project_task)
    project_task = Project_Task(id_project=projects[1].id,id_task=task21.id)
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

def peupler():
    clean()

    #Utilisateurs
    user1 = User(username="Ilian", password="ilian", mail="ilian.ben@gmail.com", role=2)
    user2 = User(username="Maxime", password="maxime", mail="maxime.b@gmail.com", role=1)
    user3 = User(username="Hugo", password="hugo", mail="hugo.b@gmail.com", role=3)
    user4 = User(username="Fouad", password="fouad", mail="fouad.l@gmail.com", role=2)
    user5 = User(username="Sophie", password="sophie", mail="sophie.p@gmail.com", role=3)
    user6 = User(username="Thibaud", password="thibaud", mail="thibaud.q@gmail.com", role=2)
    user7 = User(username="Xinlei", password="xinlei", mail="xinlei.z@gmail.com", role=2)
    user8 = User(username="Albane", password="albane", mail="albane.d@gmail.com", role=3)
    user9 = User(username="Estelle", password="estelle", mail="estelle.m@gmail.com", role=1)
    user10 = User(username="Perla", password="perla", mail="perla.el@gmail.com", role=2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)
    db.session.add(user5)
    db.session.add(user6)
    db.session.add(user7)
    db.session.add(user8)
    db.session.add(user9)
    db.session.add(user10)
    db.session.commit()

    #Projets
    project1 = Project(name="LLM dans notre intranet", description="Il s'agit d’étudier la possibilité d’utiliser l’intelligence artificielle pour faciliter la recherche d’information sur l’intranet de l’école. L’utilisateur devrait pouvoir «venir sur l’intranet, exprimer sa problématique dans son langage et ensuite avoir une réponse simple».",
                       date=datetime(2024, 4,8), manager=user2.id)
    project2 = Project(name="IMTrello", description="Créer son propre Trello",
                       date=datetime(2024, 4, 20), manager=user8.id)
    project3 = Project(name="LinkUp", description="Un engagement associatif facile et personnalisable !", date=datetime(2024, 4, 18), manager=user5.id)
    db.session.add(project1)
    db.session.add(project2)
    db.session.add(project3)
    db.session.commit()

    #Association des dvps aux projets
    for user in [user1, user2, user3,user4,user5, user6, user7]:
        project_dvp = Project_Dvp(id_project=project1.id, id_dvp=user.id)
        db.session.add(project_dvp)
    for user in [user5, user8, user9]:
        project_dvp = Project_Dvp(id_project=project2.id, id_dvp=user.id)
        db.session.add(project_dvp)
    for user in [user2, user5, user8, user10 ]:
        project_dvp = Project_Dvp(id_project=project3.id, id_dvp=user.id)
        db.session.add(project_dvp)
    db.session.commit()

    #Colonnes
    c11 = Column(name='Ressources', project=project1.id)
    c12 = Column(name='En ce moment', project=project1.id)
    c13 = Column(name='A venir', project=project1.id)
    c14 = Column(name='Fait !!!', project=project1.id)
    db.session.add(c11)
    db.session.add(c12)
    db.session.add(c13)
    db.session.add(c14)
    c21 = Column(name='Base de donnée', project=project2.id)
    c22 = Column(name='Front-end', project=project2.id)
    db.session.add(c21)
    db.session.add(c22)
    c31 = Column(name='Com.', project=project3.id)
    c32 = Column(name='Figma', project=project3.id)
    c33 = Column(name='Livrables', project=project3.id)
    db.session.add(c31)
    db.session.add(c32)
    db.session.add(c33)
    db.session.commit()

    #Tâches
    task11 = Task(name="Lancement de projet", description="But : cerner le sujet et plannification", date=datetime(2024, 3, 6), column=c14.id,
                  status='Completée', priority='Importante')
    task12 = Task(name="RB: principe des LLM", description="Recherche biblio : qu'est-ce que c'est ? Comment ça marche ?",
                  date=datetime(2024, 4, 1), column=c12.id,
                  status='En cours', priority='Importante')
    task13 = Task(name="RB: LLM existants",
                  description="Recherche biblio : qu'est-ce qui existe ? Compétences ?",
                  date=datetime(2024, 4, 1), column=c12.id,
                  status='En cours', priority='Forte')
    task14 = Task(name="RB: Réentrainement",
                  description="Recherche biblio : Comment faire ? Quels coûts ?",
                  date=datetime(2024, 4, 1), column=c12.id,
                  status='En cours', priority='Importante')
    task15 = Task(name="RB: Coûts machine virtuelle",
                  description="Recherche biblio : pour demande de budget",
                  date=datetime(2024, 4, 1), column=c12.id,
                  status='Completée', priority='Importante')
    task16 = Task(name="RB: Mise en commun",
                  description="Recherche biblio : Livrable !!!!",
                  date=datetime(2024, 4, 2), column=c13.id,
                  status='En attente', priority='Importante')
    task17 = Task(name="Calendrier",
                  description="lien vers calendrier",
                  date=datetime(2024, 2, 1), column=c11.id,
                  status='Completée', priority= 'Facultative')

    task21 = Task(name="Utilisateur",
                  description="Nom d'utilisateur, mdp, rôle, mail (et id)",
                  date=datetime(2024, 4, 1), column=c21.id,
                  status='En pause', priority='Forte')
    task22 = Task(name="Projet",
                  description="Nom, description, date, manager (et id)",
                  date=datetime(2024, 4, 1), column=c21.id,
                  status='En cours', priority='Forte')
    task23 = Task(name="Vue liste",
                  description="Liste des tâches + filtres",
                  date=datetime(2024, 4, 5), column=c22.id,
                  status='En attente', priority='Faible')
    task24 = Task(name="Connexion",
                  description="Récupérer id utilisateur + vérifier son existence sinon redirection inscription",
                  date=datetime(2024, 4, 6), column=c22.id,
                  status='En cours', priority='Forte')
    task25 = Task(name="Vue coeur",
                  description="Organiser les tâches dans un coeur",
                  date=datetime(2024, 4, 7), column=c22.id,
                  status='Annulée', priority='Faible')

    task31 = Task(name="Interviews bénévoles + assos",
                  description="Quels sont leurs pbs ?",
                  date=datetime(2024, 4, 1), column=c31.id,
                  status='En cours', priority='Forte')
    task32 = Task(name="Test utilisateurs",
                  description="Améliorations possibles ?",
                  date=datetime(2024, 4, 15), column=c31.id,
                  status='En attente', priority='Forte')
    task33 = Task(name="Livrable 1",
                  description="Résumé interviews et état de l'art",
                  date=datetime(2024, 4, 2), column=c33.id,
                  status='En cours', priority='Importante')
    task34 = Task(name="Livrable 2",
                  description="Résumé conception",
                  date=datetime(2024, 4, 6), column=c33.id,
                  status='En attente', priority='Importante')
    task35 = Task(name="V1",
                  description="Missions et Assos",
                  date=datetime(2024, 4, 10), column=c32.id,
                  status='En attente', priority='Forte')
    task36 = Task(name="V2",
                  description="Autres fonctionnalités : chat, prêt de matériel",
                  date=datetime(2024, 4, 12), column=c32.id,
                  status='En attente', priority='Faible')

    tasks = [task11, task12, task13, task14, task15, task16, task17, task21, task22, task23, task24, task25, task31,
             task32, task33, task34, task35, task36]
    for task in tasks:
        db.session.add(task)
    db.session.commit()

    #Association tâches à leur projet
    for task in tasks[:7+1]:
        project_task = Project_Task(id_project=project1.id, id_task=task.id)
        db.session.add(project_task)
    for task in tasks[8:11+1]:
        project_task = Project_Task(id_project=project2.id, id_task=task.id)
        db.session.add(project_task)
    for task in tasks[12:]:
        project_task = Project_Task(id_project=project3.id, id_task=task.id)
        db.session.add(project_task)
    db.session.commit()

    #Association dvp à leurs tâches
    for user in [user1, user2, user3,user4,user5, user6, user7]:
        task_dvp = Task_Dvp(id_task=task11.id, id_dvp=user.id)
        db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task12.id, id_dvp=user2.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task13.id, id_dvp=user4.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task14.id, id_dvp=user3.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task14.id, id_dvp=user5.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task15.id, id_dvp=user1.id)
    db.session.add(task_dvp)
    for user in [user1, user2, user3,user4,user5, user6, user7]:
        task_dvp = Task_Dvp(id_task=task16.id, id_dvp=user.id)
        db.session.add(task_dvp)
    for user in [user1, user2, user3,user4,user5, user6, user7]:
        task_dvp = Task_Dvp(id_task=task17.id, id_dvp=user.id)
        db.session.add(task_dvp)

    task_dvp = Task_Dvp(id_task=task21.id, id_dvp=user8.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task22.id, id_dvp=user5.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task23.id, id_dvp=user5.id)
    db.session.add(task_dvp)
    task_dvp = Task_Dvp(id_task=task25.id, id_dvp=user9.id)
    db.session.add(task_dvp)

    for user in [user2, user5, user8, user10 ]:
        task_dvp = Task_Dvp(id_task=task31.id, id_dvp=user.id)
        db.session.add(task_dvp)
    for user in [user5, user8]:
        task_dvp = Task_Dvp(id_task=task33.id, id_dvp=user.id)
        db.session.add(task_dvp)
    for user in [user2, user5, user8, user10 ]:
        task_dvp = Task_Dvp(id_task=task32.id, id_dvp=user.id)
        db.session.add(task_dvp)
    for user in [user2, user10 ]:
        task_dvp = Task_Dvp(id_task=task34.id, id_dvp=user.id)
        db.session.add(task_dvp)
    for user in [user5, user8]:
        task_dvp = Task_Dvp(id_task=task35.id, id_dvp=user.id)
        db.session.add(task_dvp)
    for user in [user2, user5]:
        task_dvp = Task_Dvp(id_task=task36.id, id_dvp=user.id)
        db.session.add(task_dvp)
    db.session.commit()