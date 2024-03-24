import flask

from flask import Flask, redirect, url_for, flash, jsonify
import database.database as database
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secretkey1234"

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

def formulaire_new_project(form):
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

def formulaire_new_task(form, project_id):
    devs = form.get("developpeurs", "").split(' ')
    enddate = form.get("date", "")

    result = True
    errors = []

    if enddate < date.today().strftime("%Y-%m-%d"):
        result = False
        errors += ["Date invalide"]

    if devs != ['']:
        for dev in devs:
            user = database.db.session.query(database.User).filter(database.User.mail == dev).first()
            if user is None:
                result = False
                errors += ["Une des adresses emails est incorrecte"]
                break

            elif user.role == 1:
                result = False
                errors += ["Une des personnes ajoutées n'est pas développeur"]
                break

            elif user not in database.get_dvps_of_project(project_id):
                result = False
                errors += ["Une des personnes ajoutées n'est pas dans le projet"]
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
        developpeur = [user]
        if devs != ['']:
            for d in devs:
                developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]

        result, errors = formulaire_new_project(form)

        flask.session['name'] = form.get("name", "")
        flask.session['des'] = form.get("des", "")
        flask.session['date'] = form.get("date", "")
        flask.session['dev'] = form.get("dev", "")


        if result :
            database.new_project(form.get("name", ""), form.get("description", ""),
                                 int(date[0]), int(date[1]), int(date[2]), user, developpeur)
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
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)
    semaines, mois, apres = echeances(user, projet)

    if flask.request.method == 'POST':
        form = flask.request.form
        date = form.get("date", "").split("-")
        devs = form.get("developpeur", "").split(' ')
        developpeur = [user]
        if devs != ['']:
            for d in devs:
                developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]

        result, errors = formulaire_new_project(form)

        flask.session['name'] = form.get("name", "")
        flask.session['des'] = form.get("des", "")
        flask.session['date'] = form.get("date", "")
        flask.session['dev'] = form.get("dev", "")


        if result :
            database.new_project(form.get("name", ""), form.get("description", ""),
                                 int(date[0]), int(date[1]), int(date[2]), user, developpeur)
            projets = database.projects_of_user(user)
            semaines, mois, apres = echeances(user, projet)
            return flask.render_template("home_project.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, project_id=project_id)
        else:
            # Si les données ne sont pas valides, affichez un message d'erreur ou continuez à afficher le formulaire
            return flask.render_template('error.html.jinja2', semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, errors=errors)



    else :
        print(projets)
        return flask.render_template("home_project.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, project_id=project_id)

## VUE COLONNES ##
@app.route('/<int:user_id>/colonne', methods=["GET", "POST"])
def colonne(user_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)

    if flask.request.method == 'POST':

        form = flask.request.form
        if "project" in form:
            date = form.get("date", "").split("-")
            devs = form.get("developpeur", "").split(' ')
            developpeur = [user]
            if devs != ['']:
                for d in devs:
                    developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]

            result, errors = formulaire_new_project(form)

            flask.session['name'] = form.get("name", "")
            flask.session['des'] = form.get("des", "")
            flask.session['date'] = form.get("date", "")
            flask.session['dev'] = form.get("dev", "")

            if result:
                database.new_project(form.get("name", ""), form.get("description", ""),
                                     int(date[0]), int(date[1]), int(date[2]), user, developpeur)
                projets = database.projects_of_user(user)
                return flask.render_template("colonne.html.jinja2", user=user, projects=projets)
            else:
                print('hello')
                # Si les données ne sont pas valides, affichez un message d'erreur ou continuez à afficher le formulaire
                return flask.render_template('erreurcol.html.jinja2', user=user, projects=projets, errors=errors)

    else:
        return flask.render_template("colonne.html.jinja2",  user=user, projects=projets)

@app.route('/<int:user_id>/<int:project_id>/colonne_project', methods=["GET", "POST"])
def colonne_project(user_id, project_id):




    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)

    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
    taches = [0]*len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1

    devs_taches = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
        devs_taches[i] = devs_tache


    if flask.request.method == 'POST':

        if flask.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = flask.request.get_data().decode("utf-8").split('&')
            tid = data[0]
            cid = data[1]
            task = database.db.session.get(database.Task, tid[-1])
            task.column = cid[-1]
            database.db.session.commit()
            return data


        else :
            form = flask.request.form
            if "project" in form:
                date = form.get("date", "").split("-")
                devs = form.get("developpeur", "").split(' ')
                developpeur = [user]
                if devs != ['']:
                    for d in devs:
                        developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]

                result, errors = formulaire_new_project(form)

                flask.session['name'] = form.get("name", "")
                flask.session['des'] = form.get("des", "")
                flask.session['date'] = form.get("date", "")
                flask.session['dev'] = form.get("dev", "")

                if result:
                    database.new_project(form.get("name", ""), form.get("description", ""),
                                         int(date[0]), int(date[1]), int(date[2]), user, developpeur)
                    projets = database.projects_of_user(user)
                    return flask.render_template("colonne_project.html.jinja2", user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches)
                else:
                    print('hello')
                    # Si les données ne sont pas valides, affichez un message d'erreur ou continuez à afficher le formulaire
                    return flask.render_template('erreurcolp.html.jinja2', user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches, errors=errors)

            elif "task" in form:
                date = form.get("date", "").split("-")
                devs = form.get("developpeur", "").split(' ')
                developpeur = []
                if devs != ['']:
                    for d in devs:
                        developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]
                column = database.db.session.get(database.Project, form.get("colonne", ""))

                result, errors = formulaire_new_task(form, project_id)


                if result:
                    database.new_task(user, projet, form.get("name", ""), int(date[0]), int(date[1]), int(date[2]),
                                      form.get("description", ""), column, form.get("status", ""), form.get("prio", ""),
                                      developpeur)
                    taches = [0] * len(colonnes)
                    i = 0
                    for col in colonnes:
                        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
                        i += 1

                    devs_taches = [0] * len(colonnes)
                    for i in range(len(colonnes)):
                        devs_tache = [0] * len(taches[i])
                        for j in range(len(taches[i])):
                            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
                        devs_taches[i] = devs_tache

                    return flask.render_template("colonne_project.html.jinja2", user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches)
                else:
                    # permet de sauvegarder les données en cas d'erreur ou de refresh de page
                    flask.session['name'] = form.get("name", "")
                    flask.session['des'] = form.get("des", "")
                    flask.session['date'] = form.get("date", "")
                    flask.session['dev'] = form.get("dev", "")
                    flask.session['status'] = form.get("status", "")
                    flask.session['prio'] = form.get("prio", "")
                    # Si les données ne sont pas valides, affichez un message d'erreur ou continuez à afficher le formulaire
                    return flask.render_template('erreurcolp.html.jinja2', user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches, errors=errors)

            elif "column" in form:
                database.new_column(form.get("name", ""), projet, user)
                colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
                taches = [0] * len(colonnes)
                i = 0
                for col in colonnes:
                    taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
                    i += 1

                devs_taches = [0] * len(colonnes)
                for i in range(len(colonnes)):
                    devs_tache = [0] * len(taches[i])
                    for j in range(len(taches[i])):
                        devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
                    devs_taches[i] = devs_tache

                return flask.render_template("colonne_project.html.jinja2", user=user, projects=projets,
                                             projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches)


    else:
        return flask.render_template("colonne_project.html.jinja2",  user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches)



@app.route('/<int:user_id>/<int:project_id>/developpeurs', methods=["GET", "POST"])
def developpeurs(user_id, project_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)

    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
    taches = [0] * len(colonnes)
    developpeurs = database.get_dvps_of_project(project_id)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1

    devs_taches = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
        devs_taches[i] = devs_tache

    if flask.request.method=="POST":
        form=flask.request.form
        result = True
        errors = ""

        dev = database.db.session.query(database.User).filter(database.User.mail == form["dev"]).first()
        if dev is None:
            result = False
            errors = ["L'adresse email ne correspond à aucun utilisateur"]

        elif user.role == 1:
            result = False
            errors = ["Cette personne n'est pas développeur"]

        elif user not in database.get_dvps_of_project(project_id):
            result = False
            errors = ["Cette personne n'est pas développeur sur le projet"]

        elif user in developpeurs:
            result = False
            errors = ["Cette personne est déjà sur ce projet"]

        if result:
            database.add_dvp_to_project(user, projet, dev)
            devs = database.get_dvps_of_project(projet)
            return flask.render_template('developpeurs.html.jinja2', user=user, projects=projets,
                                         projet=projet, colonnes=colonnes, taches=taches, developpeurs=devs, devs=devs_taches)
        else:
            return flask.render_template('developpeurs.html.jinja2', user=user, projects=projets,
                                         projet=projet, colonnes=colonnes, taches=taches, developpeurs=developpeurs, devs=devs_taches, errordev=errors)
    else :
        return flask.render_template("developpeurs.html.jinja2", user=user, projects=projets,
                                 projet=projet, colonnes=colonnes, taches=taches, developpeurs=developpeurs, devs=devs_taches)


@app.route('/<int:user_id>/<int:project_id>/<int:task_id>/popUp', methods=["GET", "POST"])
def popUp(user_id, project_id, task_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)

    print(projet.manager)
    print(user.id)

    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1

    devs_taches = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
        devs_taches[i] = devs_tache

    tache = database.db.session.get(database.Task, task_id)
    com = database.db.session.query(database.Comment).filter_by(task=task_id).all()
    commentaires = []
    for c in com:
        commentaires += [(c, database.db.session.get(database.User, c.author))]
    devs = database.get_dvps_of_task(task_id)

    if flask.request.method=="POST":
        form = flask.request.form
        if "formcomment" in form:
            database.new_comment(user, tache, form["comment"])
            com = database.db.session.query(database.Comment).filter_by(task=task_id).all()
            commentaires = []
            for c in com:
                commentaires += [(c, database.db.session.get(database.User, c.author))]
            print(commentaires)
            return flask.render_template('popUpTask.html.jinja2', user=user,  projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches,  tache=tache,
                                    commentaires=commentaires, developers=devs, devs=devs_taches)

        elif "formdev" in form:
            result = True
            errors = ""

            dev = database.db.session.query(database.User).filter(database.User.mail == form["dev"]).first()
            if dev is None:
                result = False
                errors = ["L'adresse email ne correspond à aucun utilisateur"]

            elif user.role == 1:
                result = False
                errors = ["Cette personne n'est pas développeur"]

            elif user not in database.get_dvps_of_project(project_id):
                result = False
                errors = ["Cette personne n'est pas développeur sur le projet"]

            elif user in database.get_dvps_of_task(task_id):
                result = False
                errors = ["Cette personne est déjà assignée à cette tâche"]


            if result:
                database.add_dvp_to_task(user, tache, dev)
                devs_taches = [0] * len(colonnes)
                for i in range(len(colonnes)):
                    devs_tache = [0] * len(taches[i])
                    for j in range(len(taches[i])):
                        devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
                    devs_taches[i] = devs_tache
                return flask.render_template('popUpTask.html.jinja2', user=user, projects=projets,
                                             projet=projet, colonnes=colonnes, taches=taches, tache=tache,
                                             commentaires=commentaires, developers=devs, devs=devs_taches)

            else:
                return flask.render_template('popUpTask.html.jinja2', user=user, projects=projets,
                                             projet=projet, colonnes=colonnes, taches=taches, tache=tache,
                                             commentaires=commentaires, developers=devs, devs=devs_taches, errordev=errors)


    else :
        return flask.render_template('popUpTask.html.jinja2', user=user,  projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches,  tache=tache,
                                    commentaires=commentaires, developers=devs, devs=devs_taches)

@app.route('/<int:user_id>/<int:project_id>/<int:task_id>/<int:dev_id>/supprdev', methods=["GET", "POST"])
def supprdev_de_tache(user_id,project_id,task_id, dev_id):
    user = database.db.session.get(database.User, user_id)
    dev = database.db.session.get(database.User, dev_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)


    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1
    tache = database.db.session.get(database.Task, task_id)

    devs_taches = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
        devs_taches[i] = devs_tache


    if flask.request.method == 'POST':
        if dev_id==user_id:
            database.delete_task(tache, user, projet)
            return"hello"
        else:
            database.delete_dvp_of_task(user, tache, dev)
            return "hello"



    return flask.render_template('supprdev.html.jinja2', user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, tache=tache, dev=dev, devs=devs_taches)


@app.route('/<int:user_id>/<int:project_id>/<int:dev_id>/supprdev', methods=["GET", "POST"])
def supprdev_de_projet(user_id, project_id, dev_id):
    user = database.db.session.get(database.User, user_id)
    dev = database.db.session.get(database.User, dev_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)


    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1

    devs_taches = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
        devs_taches[i] = devs_tache

    if flask.request.method == 'POST':
        database.delete_dvp_of_project(user, projet, dev)
        return "hello"




    return flask.render_template('supprdevp.html.jinja2', user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, dev=dev, devs=devs_taches)

@app.route('/<int:user_id>/<int:project_id>/supprproj', methods=["GET", "POST"])
def suppr_projet(user_id, project_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)


    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1

    devs_taches = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
        devs_taches[i] = devs_tache

    if flask.request.method == 'POST':
        database.delete_project(project_id, user)
        return "hello"

    return flask.render_template('supprproj.html.jinja2', user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches)


@app.route('/<int:user_id>/<int:project_id>/<int:col_id>/suppr_col', methods=["GET", "POST"])
def suppr_col(user_id, project_id, col_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)
    col = database.db.session.get(database.Column, col_id)


    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1
    devs_taches = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
        devs_taches[i] = devs_tache

    if flask.request.method == 'POST':
        database.delete_column(col, projet, user)
        return "hello"

    return flask.render_template('supprcol.html.jinja2', user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, col=col, devs=devs_taches)


if __name__ == '__main__':
    app.run()

