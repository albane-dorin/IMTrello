import flask
from flask import Flask
app = Flask(__name__)

@app.route('/')
def connexion():
    return flask.render_template("connexion.html.jinja2")





if __name__ == '__main__':
    app.run()
