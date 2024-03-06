import flask
from flask import Flask
import database

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database.db.init_app(app)

with app.test_request_context():
    database.init_database()
    app.app_context()
    database.peupler_db()

    #Test ajouter utilisateur
    database.new_user("Lovely", "coeur", "lovely@gmail", role=3)
    users = database.User.query.all()
    print(users)
    for user in users:
       print(user.id, user.username, user.password, user.mail)

    #Test ajouter project
    database.new_project('IMTrello', 'Pour UE WEB', 2024, 3,29,users[1],users)
    projects = database.Project.query.all()
    for project in projects:
      print(project.id, project.name)
    dvps_project3 = database.Project_Dvp.query.filter_by(id_project=3).all()
    for project in dvps_project3:
      print('User', project.id_dvp)
    
    #Test Ajout colonne
    print('normalement pas de colonne')
    database.new_column(name='Let s Go!', project=projects[2], user=users[2])
    cs = database.Column.query.filter_by(project=3).all()
    for c in cs:
        print(c.id, c.name)
    print('normalement une colonne')
    database.new_column(name='Let s Go!', project=projects[2], user=users[1])
    cs = database.Column.query.filter_by(project=3).all()
    for c in cs:
        print(c.id, c.name)

    #Test Ajout Tâche
    database.new_task(user=users[1], project=projects[2], name='backend', year=2024, month=3, day=28, description='Houla', column=cs[0], status =2, dvps=users)
    tasks = database.Task.query.all()
    for task in tasks:
        print(task.id, task.name)
    task_dvp = database.Task_Dvp.query.filter_by(id_task=5).all()
    print('développeur sur cette nouvelle tâche')
    for dvp in task_dvp:
        print(dvp.id_dvp)
    project_tasks = database.Project_Task.query.filter_by(id_project=3).all()
    print('les tâches du nouveaux projets')
    for t in project_tasks:
        print(t.id_project, t.id_task)

    #Test Ajout Commentaire
    database.new_comment(author=users[0], content='bla bla', task=tasks[0])
    database.new_comment(author=users[1], content='yep !', task=tasks[0])
    comments = database.Comment.query.all()
    for comment in comments:
        print(comment.id, comment.author, comment.content)