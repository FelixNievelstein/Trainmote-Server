from configparser import SafeConfigParser
import os
from . import userHelper

class ConfigController():
    parser = SafeConfigParser()
    dbFileName = '/tom-db.sqlite'
    preferencesFileName = '/sharedPreferences.ini'

    def loadPreferences(self):
        path = self.checkSettingsFile()
        if path is not None:
            self.parser.read(path)
            return True
        return False

    def checkSettingsFile(self):
        pathPreferences = self.getContentDir() + self.preferencesFileName
        if os.path.exists(pathPreferences):
            if len(self.parser.read(pathPreferences)) == 1:
                return pathPreferences
        else:
            self.createContentDir()
            self.createPreferencesFile(pathPreferences)
            if len(self.parser.read(pathPreferences)) == 1:
                return pathPreferences
        return None

    def createPreferencesFile(self, file):
        createParser = SafeConfigParser()
        createParser.add_section('info')
        createParser.set('info', 'version', '0.1')
        createParser.add_section('settings')
        dbPath = self.getContentDir() + '/tom-db.sqlite'
        createParser.set('settings', 'sqlitePath', dbPath)
        with open(file, 'w+') as iniFile:
            createParser.write(iniFile)

    def createContentDir(self):
        if not os.path.exists(self.getContentDir()):
            os.makedirs(self.getContentDir())

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
            with open(self.getContentDir() + self.preferencesFileName, 'w') as configfile:
                self.parser.write(configfile)
            return True
        except Exception as e:
            print('Error saving config: {}'.format(e))
            return False

    def getContentDir(self) -> str:
        if userHelper.is_root() is True:
            return "/content"
        else:
            return "~/content"
