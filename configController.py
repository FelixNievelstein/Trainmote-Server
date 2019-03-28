from ConfigParser import SafeConfigParser
import sys

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
        try:
            sqliteVersion = self.parser.get('settings', 'sqliteVersion')
            print()
            return sqliteVersion is not None
        except:
            return False        

    def getDataBasePath(self):
        return self.parser.get('settings', 'sqlitePath')

    def setSQLiteInstalled(self):
        try:
            self.parser.set('settings', 'sqliteVersion', '3.0')
            parser.write(sys.stdout)
            # save to a file
            with open('content/settings.ini', 'w') as configfile:
                parser.write(configfile)
            return True
        except:
            print('Error saving config')
            return False
