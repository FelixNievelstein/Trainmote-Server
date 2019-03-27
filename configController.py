from ConfigParser import SafeConfigParser

class ConfigController():
    parser = SafeConfigParser()

    def getPreferences(self):
        print(self.loadSettings())
        return None

    def loadSettings(self):
        files = ['/content/settings.ini']
        print(self.parser.read('/content/settings.ini'))
        if self.parser.read(files[0]) == 1:
            print(files)
            return files[0]
        return None