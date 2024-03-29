import projectClass


class User:
    last_id = 0

    def __init__(self, name, password):
        User.last_id = User.last_id + 1
        self.id = User.last_id
        self.id = id
        self.name = name
        self.password = password
        self.theirNotifs = []
        self.projects = []
        self.isDeveloper = False
        self.isManager = False
        
    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def get_password(self):
        return self.password

    def get_project(self):
        return self.projects

    def connect(self, trello):
        while True:
            name = input("Enter your username: ")
            password = input("Enter your password: ")
            if trello.can_get_user(name, password):
                break
            else:
                print("Nom d'utilisateur ou mot de passe incorrect, réessayez ou créez un compte")
                choix = input("1 pour réessayer, 2 pour créer un compte")
                if choix == "2": break


    def create_account(self, trello):
        name = input("Enter your username: ")
        while True:
            password = input("Enter your password: ")
            confirm = input("Enter the same password: ")  # Check the password
            if password == confirm:
                break
            else:
                print("The two password aren't the same")
        while True:
            role = input("To be Developer enter 0, to be Manager enter 1, to be Both enter 2: ")
            match role:
                case "0" | "1" | "2":
                    trello.create_account(name, password, role)
                    break
                case _:
                    print("Invalid entry")

    def suppress_account(self, trello):
        for project in trello.get_projects():
            if project.get_manager().get_id():
                print("toto")





    def addNotif(self, notif):
        self.theirNotifs.append(notif)

    def delNotif(self, notif):
        self.theirNotifs.remove(notif)

    def delAllNotifs(self):
        self.theirNotifs = []

#############################################################
class Developer(User):
    def __init__(self, name, password):
        super().__init__(name, password)
        self.isDeveloper=True

#############################################################
class Manager(User):
    def __init__(self, name, password):
        super().__init__( name, password)
        self.isManager=True

#Créer un projet vide, sans collaborateur /!\ Inputs deviendront formulaire /!\
    def create_project(self, trello):
        name = input("Enter the name of the project: ")
        description = input("Enter the description of the project: ")
        year = input("Enter the predicted year for the end of this project: ")
        month = input("Enter the predicted year for the end of this project: ")
        day = input("Enter the predicted year for the end of this project: ")
        trello.add_project(projectClass.Project(name, description, year, month, day, [], self, []))

    def suppress_project(self, trello, project):
        for user in trello.get_users():
            for p in user.projects:
                if p.id == project.id:
                    user.projects.remove(p)
        trello.projects.remove(project)


#############################################################
class ManDev(Developer, Manager):
    def __init__(self, name, password):
        Manager.__init__(self, name, password)
        Developer.__init__(self, name, password)

