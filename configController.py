from ConfigParser import SafeConfigParser

class ConfigController():
    parser = SafeConfigParser()

    def loadPreferences(self):
        path = self.checkSettingsFile()
        if path is not None:
            self.parser.read(path)
            return True            
        return False

    def checkSettingsFile(self):
        files = ['content/settings.ini']
        if len(self.parser.read(files)) == 1:
            return files[0]
        return None

    def isSQLiteInstalled(self):
        sqliteVersion = self.parser.get('settings', 'sqliteVersion')
        return sqliteVersion is not None

    def getDataBasePath(self):
        return self.parser.get('settings', 'sqlitePath')
