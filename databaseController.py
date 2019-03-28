import sqlite3
from configController import ConfigController

class DatabaseController():
    curs = None
    conn = None

    def openDatabase(self):
        config = ConfigController()
        dbPath = config.getDataBasePath()
        if dbPath is not None:
            try:
                self.conn = sqlite3.connect(dbPath)
                self.curs = conn.cursor()
                return True
            except:
                print('Error connecting database')
        return False

    def insertStopModel(self, relaisId, messId):
        if self.openDatabase():
            # Insert a row of data
            self.curs.execute("INSERT INTO TMStopModel VALUES ('','')")
            self.conn.commit()
            self.conn.close()


    
        