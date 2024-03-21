import flask
from flask import Flask
import database.database as database
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database.db.init_app(app) # (1) flask prend en compte la base de donnee
with app.test_request_context(): # (2) bloc exécuté à l'initialisation de Flask
 database.init_database()
 app.app_context()
 database.peupler_db()


@app.route('/')
def connexion():
    return flask.render_template("connexion.html.jinja2")

@app.route('/inscription')
def inscription():
    return flask.render_template("inscription.html.jinja2")


@app.route('/id/<int:user_id>/list')
def list(user_id):
    with app.app_context():
        user = database.db.session.get(database.User, user_id)
        if user is not None:
            projects = database.projects_of_user(user)
            tasks = database.get_projects_tasks(user_id)
            return flask.render_template("list.html.jinja2", tasks=tasks, projects=projects, user=user)
        else:
            # Gérer le cas où l'utilisateur n'est pas trouvé dans la base de données
            return "Utilisateur non trouvé", 404  # Retourne une réponse 404 (Not Found)


@app.route('/home')
def home():

    semaines = []
    mois = []
    apres = []

    return flask.render_template("home.html.jinja2", semaines=semaines,
                                 mois=mois, apres=apres)

if __name__ == '__main__':
    app.run()

