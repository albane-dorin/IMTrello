import flask
from flask import Flask
app = Flask(__name__)

@app.route('/')
def connexion():
    return flask.render_template("connexion.html.jinja2")

@app.route('/inscription')
def inscription():
    return flask.render_template("inscription.html.jinja2")

@app.route('/list')
def task_list():  # put application's code here
    return flask.render_template('list.html.jinja2')




if __name__ == '__main__':
    app.run()

