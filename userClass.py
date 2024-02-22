
class User :
    last_id = 0

    def __init__(self, name, password):
        User.last_id = User.last_id + 1
        self.id = User.last_id
        self.id=id
        self.name = name
        self.password = password
        self.theirNotifs = []
        self.isDeveloper = None
        self.isManager = None

    def addNotif(self, notif):
        self.theirNotifs.append()

    def delNotif(self, notif):
        self.theirNotifs

    def delAllNotifs(self):
        self.theirNotifs = []

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

