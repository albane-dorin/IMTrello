from flask import Flask
from flask import render_template

app = Flask(__name__)

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
    return render_template('vueColonne.html.jinja2', dataTask=dataTask)

@app.route('/popUpTask')
def view_popUp():
    dataTask = {
        'taskColor' : "red",
        'titreTache' : "Task Title",
        'status' : 'En cours',
        'endDate': "06/04/2024",
        'developers' : ["A", "B", "C"],
        'description' : "Task Description",
        'commentaires' : ["Task Commentaire1", "Task Commentaire2", "Task Commentaire3", "Task Commentaire4"]
    }
    return render_template('popUpTask.html.jinja2', dataTask=dataTask)

if __name__ == '__main__':
    app.run()
