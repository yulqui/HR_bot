class Bot_Exception(Exception):
    def __init__(self, adminmessage, usermessage):
        Exception.__init__(self)
        self.adminmessage = adminmessage
        self.usermessage = usermessage

class Bot_ExceptionDataBase(Bot_Exception):
    pass

class CurrentStepError(Bot_ExceptionDataBase):
    pass
