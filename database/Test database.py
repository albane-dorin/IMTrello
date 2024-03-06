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
    database.new_user("Lovely", "coeur", "lovely@gmail")
    users = database.User.query.all()
    print(users)
    for user in users:
       print(user.id, user.username, user.password, user.mail)