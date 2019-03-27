from ConfigParser import SafeConfigParser

class ConfigController():
    parser = SafeConfigParser()

    def getPreferences(self):
        path = self.checkSettingsFile()
        if path is not None:
            print(path)
            self.parser.read(path)
            print(self.parser.get('info', 'version'))
        return None

    def checkSettingsFile(self):
        files = ['content/settings.ini']
        if len(self.parser.read(files)) == 1:
            return files[0]
        return None