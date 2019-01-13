class CommandResultModel(object):
    
    def __init__(self, commandType, id, result):
        self.commandType = commandType
        self.id = id
        self.result = result