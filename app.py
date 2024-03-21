import flask

from flask import Flask, redirect, url_for, flash, jsonify
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

def formulaire_new_project(user_id, form):
    devs = form.get("developpeurs", "").split(' ')
    enddate = form.get("date", "")

    result = True
    errors = []


    if enddate < date.today().strftime("%Y-%m-%d") :
        result = False
        errors += ["Date invalide"]

    if devs != ['']:
        for dev in devs:
            user = database.db.session.query(database.User).filter(database.User.mail == dev).first()
            if user is None:
                result = False
                errors += ["Une des adresses emails est incorrecte"]
                break

            elif user.role == 1 :
                result = False
                errors += ["Une des personnes ajoutées n'est pas développeur"]
                break
    return result, errors


                                         ############ FONCTION ECHEANCES #######################



def echeances(user, projets):
    semaines = []
    mois = []
    apres = []
    today = date.today()

    #Ajout des échéances des projets
    if isinstance(projets, type([])):
        for p in projets:
            print(p.date)
            if today <= p.date <= today + timedelta(days=7):
                semaines += [(p.date, p)]
            elif today <= p.date <= today + timedelta(days=30) :
                mois += [(p.date, p)]
            elif today <= p.date > today + timedelta(days=30):
                apres += [(p.date, p)]

    else:
        if today <= projets.date <= today + timedelta(days=7):
            semaines += [(projets.date, projets)]
        elif today <= projets.date <= today + timedelta(days=30) :
            mois += [(projets.date, projets)]
        elif today <= projets.date > today + timedelta(days=30):
            apres += [(projets.date, projets)]


    #Ajout des échéances des tâches
    if isinstance(projets, type([])):
        for t in database.tasks_of_user(user):
            if today <= t.date <= today + timedelta(days=7):
                semaines += [(t.date, t, database.project_of(t))]
            elif today <= t.date <= today + timedelta(days=30) :
                mois += [(t.date, t, database.project_of(t))]
            elif today <= t.date > today + timedelta(days=30) :
                apres += [(t.date, t, database.project_of(t))]

    else:
        for t in database.tasks_of_user(user):
            if database.project_of(t).id == projets.id:
                if today <= t.date <= today + timedelta(days=7):
                    semaines += [(t.date, t, database.project_of(t))]
                elif today <= t.date <= today + timedelta(days=30) :
                    mois += [(t.date, t, database.project_of(t))]
                elif today <= t.date > today + timedelta(days=30) :
                    apres += [(t.date, t, database.project_of(t))]

    #Tri des listes par date décroissante
    semaines.sort(key=lambda a: a[0])
    mois.sort(key=lambda a: a[0])
    apres.sort(key=lambda a: a[0])
    return semaines, mois, apres



                                    ###################### VUE CONEXION/INSCRIPTION ############################



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



                                              ########################## VUE USERS ########################



## VUES HOME ##

@app.route('/<int:user_id>/home', methods=["GET", "POST"])
def home(user_id):


    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    semaines, mois, apres = echeances(user, projets)

    if flask.request.method == 'POST':
        form = flask.request.form
        date = form.get("date", "").split("-")
        devs = form.get("developpeur", "").split(' ')
        devs += [user]
        print("date = ", date)

        result, errors = formulaire_new_project(user_id, form)

        flask.session['name'] = form.get("name", "")
        flask.session['des'] = form.get("des", "")
        flask.session['date'] = form.get("date", "")
        flask.session['dev'] = form.get("dev", "")


        if result :
            database.new_project(form.get("name", ""), form.get("description", ""),
                                 int(date[0]), int(date[1]), int(date[2]), user, [])
            projets = database.projects_of_user(user)
            semaines, mois, apres = echeances(user, projets)
            return flask.render_template("home.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets)
        else:
            # Si les données ne sont pas valides, affichez un message d'erreur ou continuez à afficher le formulaire
            return flask.render_template('error.html.jinja2', semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, errors=errors)



    else :

        return flask.render_template("home.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets)



@app.route('/<int:user_id>/<int:project_id>/home_project', methods=["GET", "POST"])
def home_project(user_id, project_id):
    database.peupler_db()
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)
    semaines, mois, apres = echeances(user, projet)

    if flask.request.method == 'POST':
        form = flask.request.form
        date = form.get("date", "").split("-")
        devs = form.get("developpeur", "").split(' ')
        devs += [user]
        print("date = ", date)

        result, errors = formulaire_new_project(user_id, form)

        flask.session['name'] = form.get("name", "")
        flask.session['des'] = form.get("des", "")
        flask.session['date'] = form.get("date", "")
        flask.session['dev'] = form.get("dev", "")


        if result :
            database.new_project(form.get("name", ""), form.get("description", ""),
                                 int(date[0]), int(date[1]), int(date[2]), user, [])
            projets = database.projects_of_user(user)
            semaines, mois, apres = echeances(user, projet)
            return flask.render_template("home_project.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, project_id=project_id)
        else:
            # Si les données ne sont pas valides, affichez un message d'erreur ou continuez à afficher le formulaire
            return flask.render_template('error.html.jinja2', semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, errors=errors)



    else :

        return flask.render_template("home_project.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, project_id=project_id)

## VUE COLONNES ##
@app.route('/<int:user_id>/colonne')
def colonne(user_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)

    return flask.render_template("colonne.html.jinja2",  user=user, projects=projets)

@app.route('/<int:user_id>/<int:project_id>/colonne_project', methods=["GET", "POST"])
def colonne_project(user_id, project_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)
    return flask.render_template("colonne_project.html.jinja2",  user=user, projects=projets, projet=projet)





if __name__ == '__main__':
    app.run()

