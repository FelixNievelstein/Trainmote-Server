from configparser import SafeConfigParser
import sys
import os

class ConfigController():
    parser = SafeConfigParser()
    directory = 'content'
    pathPreferences = 'content/sharedPreferences.ini'

    def loadPreferences(self):
        path = self.checkSettingsFile()
        if path is not None:
            self.parser.read(path)
            return True
        return False

    def checkSettingsFile(self):
        if os.path.exists(self.pathPreferences):
            print("os.path.exists")
            if len(self.parser.read(self.pathPreferences)) == 1:
                return self.pathPreferences
        else:
            self.createContentDir()
            self.createPreferencesFile(self.pathPreferences)
            if len(self.parser.read(self.pathPreferences)) == 1:
                return self.pathPreferences
        return None

    def createPreferencesFile(self, file):
        print("createPreferencesFile")
        createParser = SafeConfigParser()
        createParser.add_section('info')
        createParser.set('info', 'version', '0.1')
        createParser.add_section('settings')
        createParser.set('settings', 'sqlitePath', 'content/tom-db.sqlite')
        with open(file, 'w+') as iniFile:
            print('Created Preferences Inital File')
            createParser.write(iniFile)

    def createContentDir(self):
        print("createContentDir")
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def isSQLiteInstalled(self):
        try:
            sqliteVersion = self.parser.get('settings', 'sqliteVersion')
            return sqliteVersion is not None
        except Exception as e:
            print(e)
            return False

    def getDataBasePath(self):
        if self.loadPreferences():
            return self.parser.get('settings', 'sqlitePath')
        return None

    def setSQLiteInstalled(self):
        try:
            self.parser.set('settings', 'sqliteVersion', '3.0')
            # save to a file
            with open(self.pathPreferences, 'w') as configfile:
                self.parser.write(configfile)
            return True
        except Exception as e:
            print('Error saving config: {}'.format(e))
            return False
