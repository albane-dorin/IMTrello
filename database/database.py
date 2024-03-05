from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

from database.database import db



db = SQLAlchemy()


def init_database():
    db.create_all()


#Création des tables

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    password = db.Column(db.Text)
    mail = db.Column(db.Text)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    manager = db.Column(db.Integer, ForeignKey('User.id'))

class Column(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    project = db.Column(db.Integer, ForeignKey('Project.id'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    column = db.Column(db.Integer, db.ForeignKey('Column.id'))

class Notif(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('User.id'))
    content = db.Column(db.Text)

class Project_Task(db.Model):
    id_project = db.Column(db.Integer, ForeignKey('Project.id'), primary_key=True)
    id_task = db.Column(db.Integer, ForeignKey('Task.id'), primary_key=True)

class Project_Dvp(db.Model):
    id_project = db.Column(db.Integer, ForeignKey('Project.id'), primary_key=True)
    id_dvp = db.Column(db.Integer, ForeignKey('User.id') , primary_key=True)

class Task_Dvp(db.Model):
    id_task = db.Column(db.Integer, ForeignKey , primary_key=True)
    id_dvp = db.Column(db.Integer, ForeignKey('User.id') , primary_key=True)



