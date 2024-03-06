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