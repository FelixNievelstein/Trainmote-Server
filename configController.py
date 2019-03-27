from ConfigParser import SafeConfigParser

class ConfigController():
    parser = SafeConfigParser()

    def getPreferences(self):
        print(self.checkSettingsFile())
        return None

    def checkSettingsFile(self):
        files = ['content/settings.ini']
        if len(self.parser.read(files)) == 1:
            return files[0]
        return None