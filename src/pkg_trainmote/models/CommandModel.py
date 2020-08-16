class CommandModel(object):
    
    def __init__(self, commandType, id, value):
        self.commandType = commandType
        self.id = id
        self.value = value
        self.params = dict()