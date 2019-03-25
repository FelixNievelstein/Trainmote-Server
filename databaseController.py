from configController import ConfigController

class DatabaseController():

    def __init__(self):
        config = ConfigController()
        config.getPreferences()