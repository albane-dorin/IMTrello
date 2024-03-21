import flask

from flask import Flask, redirect, url_for
import database.database as database
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database.db.init_app(app) # (1) flask prend en compte la base de donnee
with app.test_request_context(): # (2) bloc exécuté à l'initialisation de Flask
 database.init_database()
 app.app_context()
 database.peupler_db()


############# FONCTIONS FORMULAIRE #######################
def form_valide(form, i):  # 0 pour connexion, 1 pour inscription
    result = True
    errors = []

    email = flask.request.form.get("email", "")
    p1 = flask.request.form.get("password", "")

    if i == 0:

        if email == "":
            result = False

        else:

            user = database.db.session.query(database.User).filter(database.User.mail == email).first()

            if user is None:
                result = False
                errors += ["Cet email n'est lié à aucun compte. Utilisez un autre email ou inscrivez-vous."]

            else:
                mdp = user.password
                if mdp != p1:
                    result = False
                    errors += ["Mot de passe incorrect"]

    if i == 1:
        name = form.get("username", "")
        p2 = flask.request.form.get("p2", "")

        # Test de validité

        if p1 == "" or p2 == "":
            result = False

        for user in database.User.query.all():
            if user.mail == email:
                result = False
                errors += ["Cet email est déjà lié à un compte. Utilisez un autre email ou connectez vous."]

        if len(name) > 20:
            result = False
            errors += ["Le nom d'utilisateur ne peut exceder 20 caractères"]

        if p1 != p2:
            result = False
            errors += ["Les mots de passe sont différents."]

    return result, errors


############# VUE CONEXION/INSCRIPTION ############################

@app.route('/', methods=["GET", "POST"])
def connexion():
    database.peupler_db()
    form = flask.request.form
    valide, errors = form_valide(form, 0)
    if not valide:
        return flask.render_template("connexion.html.jinja2", form=form, error=errors)
    else:
        user = database.db.session.query(database.User).filter(database.User.mail == form.get("email", "")).first()
        return redirect(url_for('home', user_id=user.id))


@app.route('/inscription', methods=["GET", "POST"])
def inscription():
    database.clean()
    form = flask.request.form
    valide, errors = form_valide(form, 1)
    if not valide:
        return flask.render_template("inscription.html.jinja2", form=form, error=errors)
    else:
        database.new_user(form.get("username", ""), form.get("password", ""), form.get("email", ""),
                          role=(form.get("role", "")))

        # Tout la base de données supprimés après pour le moment pour permettre de faire des tests. A supprimer après

        user = database.db.session.query(database.User).filter(database.User.mail == form.get("email", "")).first()

        return redirect(url_for('home', user_id=user.id))  # Change to true url afterwards


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

############## VUE USERS ########################""


@app.route('/<int:user_id>/home', methods=["GET"])
def home(user_id):
    database.peupler_db()
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    semaines = []
    mois = []
    apres = []
    print('toto')
    today = date.today()

    print(projets)
    #Ajout des échéances des projets
    for p in projets:
        if today <= p.date.date() <= today + timedelta(days=7):
            semaines += [(p.date.date(), p)]
        elif today <= p.date.date() <= today + timedelta(days=30) :
            mois += [(p.date.date(), p)]
        elif today <= p.date.date() > today + timedelta(days=30):
            apres += [(p.date.date(), p)]

    #Ajout des échéances des tâches
    for t in database.tasks_of_user(user):
        if today <= t.date.date() <= today + timedelta(days=7):
            semaines += [(t.date.date(), t, database.project_of(t))]
        elif today <= t.date.date() <= today + timedelta(days=30) :
            mois += [(t.date.date(), t, database.project_of(t))]
        elif today <= t.date.date() > today + timedelta(days=30) :
            apres += [(t.date.date(), t, database.project_of(t))]

    #Tri des listes par date décroissante
    semaines.sort(key=lambda a: a[0])
    mois.sort(key=lambda a: a[0])
    apres.sort(key=lambda a: a[0])


    return flask.render_template("home.html.jinja2", semaines=semaines,
                                 mois=mois, apres=apres, user=user, projects=projets)


if __name__ == '__main__':
    app.run()

