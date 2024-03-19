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
    database.peupler()

    users = database.User.query.all()
    print(users)
    for user in users:
        print(user.id, user.username, user.password, user.mail)

    cs= database.Column.query.all()
    for c in cs:
        print(c.id, c.name)

    for task in database.Task.query.all():
        print(task.id, task.name, task.status, task.description, task.date)

    user = database.db.session.get(database.User, 5)
    print(user.username)
    for task in database.tasks_of_user(user):
        print(task.name)



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
    database.new_task(user=users[1], project=projects[2], name='backend', year=2024, month=3, day=28, description='Houla', column=cs[0], status ='Waiting', dvps=users)
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

    #Test id_project_of()
    print('Dans le projet :', database.id_project_of(tasks[4]))

    #Test ajout
    dvp_of_task = database.Project_Dvp.query.filter_by(id_project=projects[0].id).all()
    for dt in dvp_of_task:
        print(dt.id_dvp)
    database.new_user(username='Smart', password='<PASSWORD>', mail='<EMAIL>', role=3)
    user = database.User.query.order_by(database.User.id.desc()).first()
    print('Le nouvel utilisateur est:', user.id)
    database.add_dvp_to_task(user=users[1], task=tasks[0], dvp=user)
    dvp_of_task=database.Project_Dvp.query.filter_by(id_project=projects[0].id).all()
    for dt in dvp_of_task:
        print(dt.id_dvp)
    database.add_dvp_to_project(user=users[1], project=projects[0],dvp=user)
    database.add_dvp_to_task(user=users[1], task=tasks[0], dvp=user)
    dvp_of_task = database.Task_Dvp.query.filter_by(id_task=tasks[0].id).all()
    for dt in dvp_of_task:
        print(dt.id_dvp)
        
    #test projects_of_user et tasks_of_user
    list = database.projects_of_user(user=users[0])
    print(list)
    list = database.tasks_of_user(user=users[0])
    print(list)

    print('---------')
    user = database.db.session.get(database.User, 1)
    print(user)

    loves = database.get_projects_tasks(2)
    print('hola')
    print(loves)
    for love in loves:
       print('project : ', love.p_name, 'tâche:', love.t_name)

    print(database.db.session.query(database.User.mail).all())
    projects = database.projects_of_user(user)
    for project in projects:
        print('project : ', project.name)

    tasks = database.db.session.query(database.Task).all()
    for task in tasks:
        print('task : ', task.status)

    mail = user.mail
    print(mail)
    us = database.db.session.query(database.User).filter(database.User.mail == 'sos').first()
    print(us)

    loves = database.get_projects_tasks(2)
    print('hola')
    print(loves)
    #or love in loves:
    #    print('project : ', love.p_name, 'tâche:', love.t_name)

    print(database.db.session.query(database.User,database.Task_Dvp ).join(database.Task_Dvp, database.User.id==database.Task_Dvp.id_dvp).all())

    print(projects[0].date)