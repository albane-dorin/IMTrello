import flask
from flask import Flask
app = Flask(__name__)

@app.route('/')
def connexion():
    return flask.render_template("connexion.html.jinja2")

@app.route('/inscription')
def inscription():
    return flask.render_template("inscription.html.jinja2")


@app.route('/home')
def home():
    return flask.render_template("home.html.jinja2")


if __name__ == '__main__':
    app.run()


@app.route('/id/<int : user_id>/list')

def list(user_id):
    #user = Trello.onVerra!!!!!!!!
    return flask.render_template("task_list_for_user.html.jinja2")#,user=user)