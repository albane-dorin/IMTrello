import TrelloClass


class User:
    last_id = 0

    def __init__(self, name, password):
        User.last_id = User.last_id + 1
        self.id = User.last_id
        self.id = id
        self.name = name
        self.password = password
        self.isDeveloper = None
        self.isManager = None
        
        def get_name(self):
            return self.name
        
        def get_id(self):
            return self.id

        def get_password(self):
            return self.password

        def connect(self, trello):
            while True:
                name = input("Enter your username: ")
                password = input("Enter your password: ")
                if trello.can_connect_user(name, password):
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


class Developer(User):
    def __init__(self, name, password):
        super().__init__(name, password)
        self.isDeveloper=True

class Manager(User):
    def __init__(self, name, password):
        super().__init__( name, password)
        self.isManager=True

class ManDev(Developer, Manager):
    def __init__(self, name, password):
        Manager.__init__(self, name, password)
        Developer.__init__(self, name, password)

