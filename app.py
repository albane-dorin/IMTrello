import datetime

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
 database.peupler()


                                                  ############# FONCTIONS FORMULAIRE #######################


#Cette fonction permet de vérifier la validité des formulaires d'inscription et de connexion
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


#Cette fonction permet de vérifier la validité du formulaire pour créer un nouveau projet
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
                errors += ["Une des personnes ajoutées n'est pas développeur"]  #Un projet ne peut pas avoir 2 manager, un autre manager ne pourrait rien faire
                                                                                # (n'inclus pas les ManDev qui joueront le rôle de développeur)
                break
    return result, errors


#Cette fonction permet de vérifier la validité du formulaire pour créer un nouveau projet
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
                errors += ["Une des personnes ajoutées n'est pas dans le projet"]  #Un développeur doit d'abord être ajouté sur le projet avant d'être ajouté à une tâche
                break
    return result, errors


                                         ############ FONCTION ECHEANCES #######################


#Cette fonction permet de créer les listes contenant les tâches et les projets pour la vue échéances
#(mis à part pour alléger le code de home)
def echeances(user, projets):
    semaines = []
    mois = []
    apres = []
    today = date.today()


    #Format choisi : un tuple de taille 3 pour les tâches et de taille 2 pour les projets
    #cela permettra de différencié les deux objets pour adapter l'afffichage du site

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
            print(database.project_of(t))
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

    #Tri des listes par date décroissante, la date étant constamment le premier élément des n-uplet
    semaines.sort(key=lambda a: a[0])
    mois.sort(key=lambda a: a[0])
    apres.sort(key=lambda a: a[0])
    return semaines, mois, apres



                                    ###################### VUE CONEXION/INSCRIPTION ############################


#Page de connexion
@app.route('/', methods=["GET", "POST"])
def connexion():
    form = flask.request.form

    # Récupère les résultats du test du questionnaires
    valide, errors = form_valide(form, 0)

    #Formulaire incorecte : On affiche la page avec les erreurs indiquées
    if not valide:
        return flask.render_template("connexion.html.jinja2", form=form, error=errors)

    #Formulaire valide : on récupère l'utilisateur dans la base de donnée pour rediriger vers la bonne vue
    else:
        user = database.db.session.query(database.User).filter(database.User.mail == form.get("email", "")).first()
        return redirect(url_for('home', user_id=user.id))

#Page d'inscription
@app.route('/inscription', methods=["GET", "POST"])
def inscription():
    form = flask.request.form

    # Récupère les résultats du test du questionnaires
    valide, errors = form_valide(form, 1)

    #Formulaire incorecte : On affiche la page avec les erreurs indiquées
    if not valide:
        return flask.render_template("inscription.html.jinja2", form=form, error=errors)

    #Formulaire valide : On crée l'utilisateur et on le redirige vers la vue correspondant à son profil
    else:
        database.new_user(form.get("username", ""), form.get("password", ""), form.get("email", ""),
                          role=(form.get("role", "")))

        user = database.db.session.query(database.User).filter(database.User.mail == form.get("email", "")).first()

        return redirect(url_for('home', user_id=user.id))


                            ########################## VUE LISTE ########################

#route pour la liste des tâches
@app.route('/id/<int:user_id>/list')
def list(user_id):
    user = database.db.session.get(database.User, user_id)
    if user is not None:
        projects = database.projects_of_user(user)
        tasks = database.tasks_of_user(user)

        #On remplace chaque tache par un triplet (tache, projet, manager) pour faciliter l'affichage du site
        for i in range(len(tasks)):
            tasks[i] = [tasks[i], database.project_of(tasks[i]), database.db.session.get(database.User, database.project_of(tasks[i]).manager)]
        notifs = database.Notif.query.filter_by(user=user.id).all()
        return flask.render_template("list.html.jinja2", tasks=tasks, projects=projects, user=user, notifs=notifs, page_nb=3)
    else:
        # Gérer le cas où l'utilisateur n'est pas trouvé dans la base de données
        return "Utilisateur non trouvé", 404  # Retourne une réponse 404 (Not Found)



#route pour la liste des tâches avec un popup de la tâche ouvert
@app.route('/id/<int:user_id>/<int:task_id>/Taskdetail', methods=["GET", "POST"])
def taskdetail(user_id,task_id):
    user = database.db.session.get(database.User, user_id)
    if user is not None:
        projects = database.projects_of_user(user)
        tasks = database.tasks_of_user(user)

        for i in range(len(tasks)):
            tasks[i] = [tasks[i], database.project_of(tasks[i])]
        tache = database.db.session.get(database.Task, task_id)
        projet = database.project_of(tache)
        com = database.db.session.query(database.Comment).filter_by(task=task_id).all()
        commentaires = []

        #On assemble le commentaire et son auteur pour pouvoir afficher le nom de l'auteur sur le site
        for c in com:
            commentaires += [(c, database.db.session.get(database.User, c.author))]
        devs = database.get_dvps_of_task(task_id)

        #On détermine si la tâche est urgente (à faire dans la semaine) ou non
        urgent = 'non'
        if tache.date < date.today() + timedelta(days=7):
            urgent = 'oui'

        #Pour traiter les formulaires
        if flask.request.method == "POST":
            form = flask.request.form

            #Formulaires d'envoie de commentaire, pas de vérifications à faire
            if "formcomment" in form:
                database.new_comment(user, tache, form["comment"])
                com = database.db.session.query(database.Comment).filter_by(task=task_id).all()
                commentaires = []
                for c in com:
                    commentaires += [(c, database.db.session.get(database.User, c.author))]

                return flask.render_template("ListPopUp.html.jinja2", tasks=tasks, projects=projects, user=user,
                                             tache=tache, projet=projet,
                                             commentaires=commentaires, developers=devs, urgent=urgent)

        return flask.render_template("ListPopUp.html.jinja2", tasks=tasks, projects=projects, user=user, tache=tache, projet=projet,
                                     commentaires=commentaires, developers=devs, urgent=urgent)
    else:
        # Gérer le cas où l'utilisateur n'est pas trouvé dans la base de données
        return "Utilisateur non trouvé", 404




                                              ########################## VUES ECHEANCES ########################



## VUES HOME ##

#Vues de toutes les échéances lié à l'utilisateur
@app.route('/<int:user_id>/home', methods=["GET", "POST"])
def home(user_id):

    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    semaines, mois, apres = echeances(user, projets)
    notifs = database.Notif.query.filter_by(user=user.id).all()

    # Pour traiter les formulaires
    if flask.request.method == 'POST':
        form = flask.request.form
        date = form.get("date", "").split("-")
        devs = form.get("developpeurs", "").split(' ')  #Permet de séparer les adresses mails entre chaque espace (comme demandé sur le questionnaire)
                                                        #Si erreur de frappes, renverra l'erreur "Une des adresses emails est incorrecte"
        developpeur = [user]

        #Permet de passer d'une liste d'email à une liste d'utilisateur
        if devs != ['']:
            for d in devs:
                developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]

        #Récupère les résultats du test du questionnaires
        result, errors = formulaire_new_project(form)

        #Permet d'enregistré les valeurs du questionnaires pour les réafficher en cas d'erreur
        flask.session['name'] = form.get("name", "")
        flask.session['des'] = form.get("des", "")
        flask.session['date'] = form.get("date", "")
        flask.session['dev'] = form.get("dev", "")

        # Formulaire valide : On crée le projet, redefinit les listes de projets et d'échéances et on renvoit l'utilisateur sur home
        if result :
            database.new_project(form.get("name", ""), form.get("description", ""),
                                 int(date[0]), int(date[1]), int(date[2]), user, developpeur)
            projets = database.projects_of_user(user)
            semaines, mois, apres = echeances(user, projets)
            notifs = database.Notif.query.filter_by(user=user.id).all()
            return flask.render_template("home.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, notifs=notifs)

        # Formulaire incorecte : On redirige vers une page affichant les erreurs
        # Solutions retenues afin de ne pas perdre les données du formulaire (Si description très longue par exemple)
        else:
            return flask.render_template('erreur_form_de_home.html.jinja2', semaines=semaines,
                                         mois=mois, apres=apres, user=user, projects=projets, errors=errors)

    #Vue de base renvoyé par Get
    else :

        return flask.render_template("home.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, notifs=notifs, page_nb=1)


#Vues des échéances d'un projet de l'utilisateur
@app.route('/<int:user_id>/<int:project_id>/home_project', methods=["GET", "POST"])
def home_project(user_id, project_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)
    semaines, mois, apres = echeances(user, projet)
    notifs = database.Notif.query.filter_by(user=user.id).all()

    # Pour traiter les formulaires
    if flask.request.method == 'POST':
        form = flask.request.form
        date = form.get("date", "").split("-")
        devs = form.get("developpeurs", "").split(' ')    #Permet de séparer les adresses mails entre chaque espace (comme demandé sur le questionnaire)
                                                          #Si erreur de frappes, renverra l'erreur "Une des adresses emails est incorrecte"
        developpeur = [user]


        #Permet de passer d'une liste d'email à une liste d'utilisateur
        if devs != ['']:
            for d in devs:
                developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]


        #Récupère les résultats du test du questionnaires
        result, errors = formulaire_new_project(form)

        #Permet d'enregistré les valeurs du questionnaires pour les réafficher en cas d'erreur
        flask.session['name'] = form.get("name", "")
        flask.session['des'] = form.get("des", "")
        flask.session['date'] = form.get("date", "")
        flask.session['dev'] = form.get("dev", "")

        # Formulaire valide : On crée le projet, redefinit les listes de projets et d'échéances et on renvoit l'utilisateur sur home
        if result :
            database.new_project(form.get("name", ""), form.get("description", ""),
                                 int(date[0]), int(date[1]), int(date[2]), user, developpeur)
            projets = database.projects_of_user(user)
            semaines, mois, apres = echeances(user, projet)
            notifs = database.Notif.query.filter_by(user=user.id).all()
            return flask.render_template("home_project.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, projet=projet, notifs=notifs)


        # Formulaire incorecte : On redirige vers une page affichant les erreurs
        # Solutions retenues afin de ne pas perdre les données du formulaire (Si description très longue par exemple)
        else:
            return flask.render_template('erreur_form_de_home.html.jinja2', semaines=semaines,
                                         mois=mois, apres=apres, user=user, projects=projets, errors=errors)


    #Vue de base renvoyé par Get
    else :
        return flask.render_template("home_project.html.jinja2", semaines=semaines,
                                     mois=mois, apres=apres, user=user, projects=projets, projet=projet, notifs=notifs, page_nb=4)



# Fonction de suppression des notifications, last_page permet de renvoyer à la page précédente
@app.post('/<int:user_id>/<int:last_page>/<int:notif_id>/<int:project_id>/delete/')
def delete(user_id, notif_id, last_page, project_id):
    notif = database.Notif.query.get_or_404(notif_id)
    database.db.session.delete(notif)
    database.db.session.commit()
    if last_page==1 :
        return redirect(url_for('home', user_id=user_id))
    if last_page==2 :
        return redirect(url_for('colonne', user_id=user_id))
    if last_page==3:
        return redirect(url_for('list', user_id=user_id))
    if last_page==4:
        return redirect(url_for('home_project', user_id=user_id, project_id=project_id))
    if last_page==5:
        return redirect(url_for('colonne_project', user_id=user_id, project_id=project_id))


                                                ########################## VUES PROJETS ########################

## VUE COLONNES ##

#Vues par défaut sans projet de sélectionné
@app.route('/<int:user_id>/colonne', methods=["GET", "POST"])
def colonne(user_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    notifs = database.Notif.query.filter_by(user=user.id).all()

    # Pour traiter les formulaires
    if flask.request.method == 'POST':

        form = flask.request.form

        #Pour différencier les différents formulaires
        if "project" in form:
            date = form.get("date", "").split("-")
            devs = form.get("developpeurs", "").split(' ')#Permet de séparer les adresses mails entre chaque espace (comme demandé sur le questionnaire)
                                                          #Si erreur de frappes, renverra l'erreur "Une des adresses emails est incorrecte"
            developpeur = [user]

            # Permet de passer d'une liste d'email à une liste d'utilisateur
            if devs != ['']:
                for d in devs:
                    developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]

            #Récupère les résultats du test du questionnaires
            result, errors = formulaire_new_project(form)

            # Permet d'enregistré les valeurs du questionnaires pour les réafficher en cas d'erreur
            flask.session['name'] = form.get("name", "")
            flask.session['des'] = form.get("des", "")
            flask.session['date'] = form.get("date", "")
            flask.session['dev'] = form.get("dev", "")

            # Formulaire valide : On crée le projet, redefinit les listes de projets et d'échéances et on renvoit l'utilisateur sur home
            if result:
                database.new_project(form.get("name", ""), form.get("description", ""),
                                     int(date[0]), int(date[1]), int(date[2]), user, developpeur)
                projets = database.projects_of_user(user)
                notifs = database.Notif.query.filter_by(user=user.id).all()
                return flask.render_template("colonne.html.jinja2", user=user, projects=projets, notifs=notifs)

            # Formulaire incorecte : On redirige vers une page affichant les erreurs
            # Solutions retenues afin de ne pas perdre les données du formulaire (Si description très longue par exemple)
            else:
                return flask.render_template('erreur_for_de_colonne.html.jinja2', user=user, projects=projets, errors=errors)


    #Vue de base renvoyé par Get
    else:
        return flask.render_template("colonne.html.jinja2",  user=user, projects=projets, notifs=notifs, page_nb=2)

@app.route('/<int:user_id>/<int:project_id>/colonne_project', methods=["GET", "POST"])
def colonne_project(user_id, project_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)
    notifs = database.Notif.query.filter_by(user=user.id).all()

    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()


    # On crée une list taches où taches[colonne] fournira la liste des tâches de la colonne
    taches = [0]*len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1



    # On crée une liste développeurs ou développeurs[colonne][tache] forunira la liste de développeurs de la tâche
    # On crée une liste urgents où urgents[colonne][tache] indiquera si la tâche est urgente ou non

    devs_taches = [0] * len(colonnes)

    urgents = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        urgentcol = ['non']*len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
            if taches[i][j].date < datetime.date.today() + timedelta(days=7):
                urgentcol[j] = 'oui'
        devs_taches[i] = devs_tache
        urgents[i] = urgentcol


    # Pour traiter les formulaires et les requètes ajax
    if flask.request.method == 'POST':


        #Réponse au post envoyé suite au drag and drop
        if flask.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = flask.request.get_data().decode("utf-8").split('&')
            tid = data[0].replace("id=t", "")
            print(tid)
            cid = data[1].replace("elid=col", "")
            print(cid)
            task = database.db.session.get(database.Task, tid)
            print(task)
            task.column = cid
            database.db.session.commit()
            return data


        else :
            form = flask.request.form

            # Pour différencier les différents formulaires
            if "project" in form:                                       # Formulaire nouveau projet
                date = form.get("date", "").split("-")
                devs = form.get("developpeurs", "").split(' ')
                developpeur = [user]
                if devs != ['']:
                    for d in devs:
                        developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]

                result, errors = formulaire_new_project(form)

                # Permet d'enregistré les valeurs du questionnaires pour les réafficher en cas d'erreur
                flask.session['name'] = form.get("name", "")
                flask.session['des'] = form.get("des", "")
                flask.session['date'] = form.get("date", "")
                flask.session['dev'] = form.get("dev", "")

                # Formulaire valide : On crée le projet, redefinit les listes de projets et d'échéances et on renvoit l'utilisateur sur home
                if result:
                    database.new_project(form.get("name", ""), form.get("description", ""),
                                         int(date[0]), int(date[1]), int(date[2]), user, developpeur)
                    projets = database.projects_of_user(user)
                    return flask.render_template("colonne_project.html.jinja2", user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches, urgents=urgents, notifs=notifs)


                # Formulaire incorecte : On redirige vers une page affichant les erreurs
                # Solutions retenues afin de ne pas perdre les données du formulaire (Si description très longue par exemple)
                else:
                    return flask.render_template('erreur_form_de_colonne_project.html.jinja2', user=user, projects=projets,
                                                 projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches, errors=errors, urgents=urgents)



            elif "task" in form:                                       # Formulaire nouvelle tache

                date = form.get("date", "").split("-")
                devs = form.get("developpeurs", "").split(' ')
                developpeur = []
                if devs != ['']:
                    for d in devs:
                        developpeur += [database.db.session.query(database.User).filter(database.User.mail == d).first()]
                column = database.db.session.get(database.Column, form.get("colonne", ""))



                result, errors = formulaire_new_task(form, project_id)

                # Permet d'enregistré les valeurs du questionnaires pour les réafficher en cas d'erreur
                flask.session['name'] = form.get("name", "")
                flask.session['des'] = form.get("des", "")
                flask.session['date'] = form.get("date", "")
                flask.session['dev'] = form.get("dev", "")
                flask.session['status'] = form.get("status", "")
                flask.session['prio'] = form.get("prio", "")



                # Formulaire valide : On crée la tache et on met à jour les listes liés aux tâches
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
                    urgents = [0] * len(colonnes)
                    for i in range(len(colonnes)):
                        devs_tache = [0] * len(taches[i])
                        urgentcol = ['non'] * len(taches[i])
                        for j in range(len(taches[i])):
                            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
                            if taches[i][j].date < datetime.date.today() + timedelta(days=7):
                                urgentcol[j] = 'oui'
                        devs_taches[i] = devs_tache
                        urgents[i] = urgentcol


                    return flask.render_template("colonne_project.html.jinja2", user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches, urgents=urgents, notifs=notifs)

                # Formulaire incorecte : On redirige vers une page affichant les erreurs
                # Solutions retenues afin de ne pas perdre les données du formulaire (Si description très longue par exemple)
                else:

                    return flask.render_template('erreur_form_de_colonne_project.html.jinja2', user=user, projects=projets,
                                                 projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches, errors=errors, urgents=urgents)




            elif "column" in form:                                       # Formulaire nouvelle colonne, pas de vérification nécessaire

                #On crée la colonne et on met à jour les listes liés aux colonnes et donc aux tâches

                database.new_column(form.get("name", ""), projet, user)
                colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
                taches = [0] * len(colonnes)
                i = 0
                for col in colonnes:
                    taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
                    i += 1

                devs_taches = [0] * len(colonnes)
                urgents = [0] * len(colonnes)
                for i in range(len(colonnes)):
                    devs_tache = [0] * len(taches[i])
                    urgentcol = ['non'] * len(taches[i])
                    for j in range(len(taches[i])):
                        devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
                        if taches[i][j].date < datetime.date.today() + timedelta(days=7):
                            urgentcol[j] = 'oui'
                    devs_taches[i] = devs_tache
                    urgents[i] = urgentcol

                return flask.render_template("colonne_project.html.jinja2", user=user, projects=projets,
                                             projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches, urgents=urgents, notifs=notifs)


    #Vue de base renvoyé par Get
    else:
        return flask.render_template("colonne_project.html.jinja2",  user=user, projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches, urgents=urgents, notifs=notifs, page_nb=5)



#Vue affichant les Développeurs du projet (et permet au manager de modifier la liste
@app.route('/<int:user_id>/<int:project_id>/developpeurs', methods=["GET", "POST"])
def developpeurs(user_id, project_id):

    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)
    manager = database.db.session.get(database.User, projet.manager)

    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()
    developpeurs = database.get_dvps_of_project(project_id)


    # On crée une list taches où taches[colonne] fournira la liste des tâches de la colonne
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1
        devs_taches = [0] * len(colonnes)

    # On crée une liste développeurs ou développeurs[colonne][tache] forunira la liste de développeurs de la tâche
    # On crée une liste urgents où urgents[colonne][tache] indiquera si la tâche est urgente ou non
    urgents = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        urgentcol = ['non'] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
            if taches[i][j].date < datetime.date.today() + timedelta(days=7):
                urgentcol[j] = 'oui'
        devs_taches[i] = devs_tache
        urgents[i] = urgentcol


    # Pour traiter les formulaires et les requètes ajax
    if flask.request.method=="POST":
        form=flask.request.form
        result = True
        errors = ""

        dev = database.db.session.query(database.User).filter(database.User.mail == form["dev"]).first()
        if dev is None:
            result = False
            errors = ["L'adresse email ne correspond à aucun utilisateur"]

        elif dev.role == 1:
            result = False
            errors = ["Cette personne n'est pas développeur"]

        elif dev in developpeurs:
            result = False
            errors = ["Cette personne est déjà sur ce projet"]

        if result:
            database.add_dvp_to_project(user, projet, dev)
            devs = database.get_dvps_of_project(projet.id)
            return flask.render_template('vue_developpeurs_de_projet.html.jinja2', user=user, projects=projets, manager=manager,
                                         projet=projet, colonnes=colonnes, taches=taches, developpeurs=devs, devs=devs_taches, urgents=urgents)
        else:
            return flask.render_template('vue_developpeurs_de_projet.html.jinja2', user=user, projects=projets, manager=manager,
                                         projet=projet, colonnes=colonnes, taches=taches, developpeurs=developpeurs, devs=devs_taches, errordev=errors, urgents=urgents)

    #Vue de base renvoyé par Get
    else :
        return flask.render_template("vue_developpeurs_de_projet.html.jinja2", user=user, projects=projets, manager=manager,
                                     projet=projet, colonnes=colonnes, taches=taches, developpeurs=developpeurs, devs=devs_taches, urgents=urgents)


#Vue affichant les détails d'une tâche en pop-up par dessus la vue par projet
@app.route('/<int:user_id>/<int:project_id>/<int:task_id>/popUp', methods=["GET", "POST"])
def popUp(user_id, project_id, task_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)


    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()

    # On crée une list taches où taches[colonne] fournira la liste des tâches de la colonne
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1

    # On crée une liste développeurs ou développeurs[colonne][tache] forunira la liste de développeurs de la tâche
    # On crée une liste urgents où urgents[colonne][tache] indiquera si la tâche est urgente ou non
    devs_taches = [0] * len(colonnes)
    urgents = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        urgentcol = ['non'] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
            if taches[i][j].date < datetime.date.today() + timedelta(days=7):
                urgentcol[j] = 'oui'
        devs_taches[i] = devs_tache
        urgents[i] = urgentcol

    tache = database.db.session.get(database.Task, task_id)

    # On assemble le commentaire et son auteur pour pouvoir afficher le nom de l'auteur sur le site
    com = database.db.session.query(database.Comment).filter_by(task=task_id).all()
    commentaires = []
    for c in com:
        commentaires += [(c, database.db.session.get(database.User, c.author))]
    devs = database.get_dvps_of_task(task_id)

    # On détermine si la tâche est urgente (à faire dans la semaine) ou non
    urgent = 'non'
    if tache.date < date.today() + timedelta(days=7):
        urgent= 'oui'


    # Pour traiter les formulaires et les requètes ajax
    if flask.request.method=="POST":
        form = flask.request.form

        # Formulaires d'envoie de commentaire, pas de vérifications à faire
        if "formcomment" in form:
            database.new_comment(user, tache, form["comment"])
            com = database.db.session.query(database.Comment).filter_by(task=task_id).all()
            commentaires = []
            for c in com:
                commentaires += [(c, database.db.session.get(database.User, c.author))]

            return flask.render_template('popUpTask.html.jinja2', user=user,  projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches,  tache=tache,
                                    commentaires=commentaires, developers=devs, devs=devs_taches, urgent=urgent, urgents=urgents)

        #Formulaire d'ajout de développeurs
        elif "formdev" in form:
            result = True
            errors = ""

            dev = database.db.session.query(database.User).filter(database.User.mail == form["dev"]).first()
            if dev is None:
                result = False
                errors = ["L'adresse email ne correspond à aucun utilisateur"]

            elif dev.role == 1:
                result = False
                errors = ["Cette personne n'est pas développeur"]

            elif dev not in database.get_dvps_of_project(project_id):
                result = False
                errors = ["Cette personne n'est pas développeur sur le projet"]   #Un utiliateur doit être présent sur le projet avant de pouvoir être ajouter à une tâche

            elif dev in database.get_dvps_of_task(task_id):
                result = False
                errors = ["Cette personne est déjà assignée à cette tâche"]

            # Formulaire valide : On ajoute le développeur à la tâche et on met à jour les listes lié aux développeurs
            if result:
                database.add_dvp_to_task(user, tache, dev)
                devs_taches = [0] * len(colonnes)
                for i in range(len(colonnes)):
                    devs_tache = [0] * len(taches[i])
                    for j in range(len(taches[i])):
                        devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
                    devs_taches[i] = devs_tache
                devs = database.get_dvps_of_task(task_id)
                return flask.render_template('popUpTask.html.jinja2', user=user, projects=projets,
                                             projet=projet, colonnes=colonnes, taches=taches, tache=tache,
                                             commentaires=commentaires, developers=devs, devs=devs_taches, urgent=urgent, urgents=urgents)

            # Formulaire incorecte : On affiche la page avec les erreurs indiquées
            else:
                return flask.render_template('popUpTask.html.jinja2', user=user, projects=projets,
                                             projet=projet, colonnes=colonnes, taches=taches, tache=tache,
                                             commentaires=commentaires, developers=devs, devs=devs_taches, errordev=errors, urgent=urgent, urgents=urgents)


        # Formulaire de modification de statut de la tâche (pas de vérification nécessaire)
        elif "formstatus" in form:
            print(tache.status)
            ancien_status = tache.status
            tache.status = form["status"]

            #  Envoie de notification pour prévenir de ce changement
            for dev in devs :
                database.db.session.add(database.Notif(user=dev.id, link_task=tache.id, link_project=projet.id,
                              content="La tâche " + tache.name + " du projet" + projet.name + " est passé du status "
                            + ancien_status + " au status " + tache.status))
                database.db.session.commit()

            return flask.render_template('popUpTask.html.jinja2', user=user,  projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches,  tache=tache,
                                    commentaires=commentaires, developers=devs, devs=devs_taches, urgent=urgent, urgents=urgents)


        # Formulaire de modification de priorité de la tâche (pas de vérification nécessaire)
        elif "formprio" in form:
            ancien_prio = tache.priority
            tache.priority = form["prio"]

            #  Envoie de notification pour prévenir de ce changement
            for dev in devs :
                database.db.session.add(database.Notif(user=dev.id, link_task=tache.id, link_project=projet.id,
                          content="La tâche " + tache.name + " du projet" + projet.name + " est passé de la priorité "
                        + ancien_prio + " à la priorité " + tache.priority))
                database.db.session.commit()
            return flask.render_template('popUpTask.html.jinja2', user=user,  projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches,  tache=tache,
                                    commentaires=commentaires, developers=devs, devs=devs_taches, urgent=urgent, urgents=urgents)

    #Vue de base renvoyé par Get
    else :
        return flask.render_template('popUpTask.html.jinja2', user=user,  projects=projets,
                                     projet=projet, colonnes=colonnes, taches=taches,  tache=tache,
                                    commentaires=commentaires, developers=devs, devs=devs_taches, urgent=urgent, urgents=urgents)


#Vue afficahnt le Pop-up de confirmation pour la suppression de developpeurs d'une tâche ou la suppression d'une tache
@app.route('/<int:user_id>/<int:project_id>/<int:task_id>/<int:dev_id>/supprdev', methods=["GET", "POST"])
def supprdev_de_tache(user_id,project_id,task_id, dev_id):

    user = database.db.session.get(database.User, user_id)
    dev = database.db.session.get(database.User, dev_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)


    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()

    # On crée une list taches où taches[colonne] fournira la liste des tâches de la colonne
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1
    tache = database.db.session.get(database.Task, task_id)

    # On crée une liste développeurs ou développeurs[colonne][tache] forunira la liste de développeurs de la tâche
    # On crée une liste urgents où urgents[colonne][tache] indiquera si la tâche est urgente ou non
    devs_taches = [0] * len(colonnes)
    urgents = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        urgentcol = ['non'] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
            if taches[i][j].date < datetime.date.today() + timedelta(days=7):
                urgentcol[j] = 'oui'
        devs_taches[i] = devs_tache
        urgents[i] = urgentcol

    # Pour traiter les formulaires et les requètes ajax
    if flask.request.method == 'POST':
        if dev_id==user_id:                 #Le manager ne peut se supprimer lui-même, ainsi si dev=user ça signifit que l'on souhaite supprimer la tâche et non le developpeur
            database.delete_task(tache, user, projet)       #On supprime la tâche
            return"hello"                   #Retour à la vue de base via la réponse de la requête ajax
        else:
            database.delete_dvp_of_task(user, tache, dev)   #On retire le développeur de sur cette tâche
            return "hello"                  #Retour à la vue de base via la réponse de la requête ajax


    #Si get : affiche le message de confirmation
    return flask.render_template('suppr_tache_et_dev.html.jinja2', user=user, projects=projets,
                                 projet=projet, colonnes=colonnes, taches=taches, tache=tache, dev=dev, devs=devs_taches, urgents=urgents)


#Vue afficahnt le Pop-up de confirmation pour la suppression de développeur d'un projet
@app.route('/<int:user_id>/<int:project_id>/<int:dev_id>/supprdev', methods=["GET", "POST"])
def supprdev_de_projet(user_id, project_id, dev_id):
    user = database.db.session.get(database.User, user_id)
    dev = database.db.session.get(database.User, dev_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)


    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()

    # On crée une list taches où taches[colonne] fournira la liste des tâches de la colonne
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1

    # On crée une liste développeurs ou développeurs[colonne][tache] forunira la liste de développeurs de la tâche
    # On crée une liste urgents où urgents[colonne][tache] indiquera si la tâche est urgente ou non
    devs_taches = [0] * len(colonnes)
    urgents = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        urgentcol = ['non'] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
            if taches[i][j].date < datetime.date.today() + timedelta(days=7):
                urgentcol[j] = 'oui'
        devs_taches[i] = devs_tache
        urgents[i] = urgentcol

    # Pour traiter les formulaires et les requètes ajax
    if flask.request.method == 'POST':
        database.delete_dvp_of_project(user, projet, dev)
        return "hello"                  #Retour à la vue de base via la réponse de la requête ajax



    #Si get : affiche le message de confirmation
    return flask.render_template('suppr_dev_de_projet.html.jinja2', user=user, projects=projets,
                                 projet=projet, colonnes=colonnes, taches=taches, dev=dev, devs=devs_taches, urgents=urgents)


#Vue afficahnt le Pop-up de confirmation pour la suppression d'un projet
@app.route('/<int:user_id>/<int:project_id>/supprproj', methods=["GET", "POST"])
def suppr_projet(user_id, project_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)


    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()

    # On crée une list taches où taches[colonne] fournira la liste des tâches de la colonne
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1

    # On crée une liste développeurs ou développeurs[colonne][tache] forunira la liste de développeurs de la tâche
    # On crée une liste urgents où urgents[colonne][tache] indiquera si la tâche est urgente ou non
    devs_taches = [0] * len(colonnes)
    urgents = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        urgentcol = ['non'] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
            if taches[i][j].date < datetime.date.today() + timedelta(days=7):
                urgentcol[j] = 'oui'
        devs_taches[i] = devs_tache
        urgents[i] = urgentcol

    # Pour traiter les formulaires et les requètes ajax
    if flask.request.method == 'POST':
        database.delete_project(project_id, user)
        return "hello"                  #Retour à la vue de base via la réponse de la requête ajax

    #Si get : affiche le message de confirmation
    return flask.render_template('suppr_projet.html.jinja2', user=user, projects=projets,
                                 projet=projet, colonnes=colonnes, taches=taches, devs=devs_taches, urgents=urgents)


#Vue afficahnt le Pop-up de confirmation pour la suppression d'une colonne
@app.route('/<int:user_id>/<int:project_id>/<int:col_id>/suppr_col', methods=["GET", "POST"])
def suppr_col(user_id, project_id, col_id):
    user = database.db.session.get(database.User, user_id)
    projets = database.projects_of_user(user)
    projet = database.db.session.get(database.Project, project_id)
    col = database.db.session.get(database.Column, col_id)


    colonnes = database.db.session.query(database.Column).filter_by(project=project_id).all()

    # On crée une list taches où taches[colonne] fournira la liste des tâches de la colonne
    taches = [0] * len(colonnes)
    i = 0
    for col in colonnes:
        taches[i] = database.db.session.query(database.Task).filter_by(column=colonnes[i].id).all()
        i += 1

    # On crée une liste développeurs ou développeurs[colonne][tache] forunira la liste de développeurs de la tâche
    # On crée une liste urgents où urgents[colonne][tache] indiquera si la tâche est urgente ou non
    devs_taches = [0] * len(colonnes)
    urgents = [0] * len(colonnes)
    for i in range(len(colonnes)):
        devs_tache = [0] * len(taches[i])
        urgentcol = ['non'] * len(taches[i])
        for j in range(len(taches[i])):
            devs_tache[j] = database.get_dvps_of_task(taches[i][j].id)
            if taches[i][j].date < datetime.date.today() + timedelta(days=7):
                urgentcol[j] = 'oui'
        devs_taches[i] = devs_tache
        urgents[i] = urgentcol


    # Pour traiter les formulaires et les requètes ajax
    if flask.request.method == 'POST':
        database.delete_column(col, projet, user)
        return "hello"                  #Retour à la vue de base via la réponse de la requête ajax

    #Si get : affiche le message de confirmation
    return flask.render_template('suppr_colonne.html.jinja2', user=user, projects=projets,
                                 projet=projet, colonnes=colonnes, taches=taches, col=col, devs=devs_taches, urgents=urgents)


if __name__ == '__main__':
    app.run()

