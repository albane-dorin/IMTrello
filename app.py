from flask import Flask
from flask import render_template
import database.database as database

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database.db.init_app(app) # (1) flask prend en compte la base de donnee
with app.test_request_context(): # (2) bloc exécuté à l'initialisation de Flask
 database.init_database()
 app.app_context()
 database.peupler_db()


@app.route('/')

def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/vueColonne')
def view_colonne():
    dataTask = {
        'taskColor' : "red",
        'titreTache' : "Task Title",
        'endDate': "06/04/2024",
        'developers' : ["A", "B", "C"]

    }
    return render_template('miniatureColonne.html.jinja2', dataTask=dataTask)

@app.route('/popUpTask')
def view_popUp():
    dataTask = {
        'taskColor' : "red",
        'priorite': 'absolue',
        'prioriteColor' : "red",
        'titreTache' : "Task Title",
        'status' : 'En cours',
        'endDate': "06/04/2024",
        'developers' : ["A", "B", "C"]*8,
        'description' : "Task Description<br>feezfui<br>dfai<br>dcao<br>dyufia<br>dyiuz"*4,
        'commentaires' : ["Task Commentaire1", "Task Commentaire2", "Task Commentaire3", "Task Commentaire4"]*2
    }
    return render_template('popUpTask.html.jinja2', dataTask=dataTask)

if __name__ == '__main__':
    app.run()

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

if __name__ == '__main__':
    app.run()

