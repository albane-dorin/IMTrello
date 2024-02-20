
class User :
    def __init__(self, id, name, password):
        self.id=id
        self.name = name
        self.password = password
        self.isDeveloper = None
        self.isManager = None

class Developer(User):
    def __init__(self, id, name, password):
        super().__init__(id, name, password)
        self.isDeveloper=True

class Manager(User):
    def __init__(self, id, name, password):
        super().__init__(id, name, password)
        self.isManager=True

class ManDev(Developer, Manager):
    def __init__(self, id, name, password):
        Manager.__init__(self, id, name, password)
        Developer.__init__(self, id, name, password)

