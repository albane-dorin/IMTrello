import flask
from flask import Flask
from database.database import db, init_database

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app) # (1) flask prend en compte la base de donnee
with app.test_request_context(): # (2) bloc exécuté à l'initialisation de Flask
 init_database()


@app.route('/')
def connexion():
    return flask.render_template("connexion.html.jinja2")

@app.route('/inscription')
def inscription():
    return flask.render_template("inscription.html.jinja2")





if __name__ == '__main__':
    app.run()


@app.route('/id/<int : user_id>/list')

def list(user_id):
    #user = Trello.onVerra!!!!!!!!
    return flask.render_template("task_list_for_user.html.jinja2")#,user=user)