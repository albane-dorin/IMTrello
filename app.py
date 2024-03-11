import flask
from flask import Flask, redirect
import database.database as database

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database.db.init_app(app) # (1) flask prend en compte la base de donnee

with app.test_request_context(): # (2) bloc exécuté à l'initialisation de Flask
    database.init_database()



############# FONCTIONS FORMULAIRE #######################
def form_valide(form, i ):     # 0 pour connexion, 1 pour inscription
    result = True
    errors = []


    email = flask.request.form.get("email", "")
    p1 = flask.request.form.get("password", "")

    print(i)

    if i==0:

        if email == "":
            result = False

        else:


            mails = []
            mdp = None
            #Test de validité
            for user in database.User.query.all():
                mails += [user.mail]
                if user.mail == email:
                    mdp = user.password


            if email not in mails:
                result = False
                errors += ["Cet email n'est lié à aucun compte. Utilisez un autre email ou inscrivez-vous."]

            elif mdp is None or mdp != p1 :
                result = False
                errors += ["Mot de passe incorrect"]


    if i==1:
        name = form.get("username", "")
        p2 = flask.request.form.get("p2", "")

        #Test de validité

        if p1 == "" or p2 == "" :
            result = False

        for user in database.User.query.all() :
            if user.mail == email :
                result = False
                errors += ["Cet email est déjà lié à un compte. Utilisez un autre email ou connectez vous."]

        if len(name) > 20 :
            result = False
            errors += ["Le nom d'utilisateur ne peut exceder 20 caractères"]

        if p1 != p2 :
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
        return redirect("/inscription")



@app.route('/inscription', methods=["GET", "POST"])
def inscription():

    database.clean()
    form = flask.request.form
    valide, errors = form_valide(form, 1)
    if not valide:
        return flask.render_template("inscription.html.jinja2", form=form, error=errors)
    else:
        database.new_user(form.get("username", ""), form.get("password", ""), form.get("email", ""), role=(form.get("role", "")))

        #Tout la base de données supprimés après pour le moment pour permettre de faire des tests. A supprimer après
        database.clean()

        return redirect("/") #Change to true url afterwards


############## VUE USERS ########################""

@app.route('/home')
def home():
    semaines = []
    mois = []
    apres = []

    return flask.render_template("home.html.jinja2", semaines=semaines,
                                 mois=mois, apres=apres)



if __name__ == '__main__':
    app.run()


@app.route('/id/<int : user_id>/list')

def list(user_id):
    #user = Trello.onVerra!!!!!!!!
    return flask.render_template("task_list_for_user.html.jinja2")#,user=user)