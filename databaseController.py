import sqlite3
import os
from configController import ConfigController

class DatabaseController():
    curs = None
    conn = None

    def openDatabase(self):
        config = ConfigController()
        dbPath = config.getDataBasePath()
        if dbPath is not None:
            if not os.path.exists(dbPath):
                self.createInitalDatabse(dbPath)
            
            try:
                self.conn = sqlite3.connect(dbPath)
                print(self.conn)
                self.curs = self.conn.cursor()
                print(self.curs)
                return True
            except Exception as e: 
                print(e)
                print('Error connecting database')
        return False

    def createInitalDatabse(self, dbPath):
        connection = sqlite3.connect(dbPath)
        cursor = connection.cursor()
        sqlStatementStop = 'CREATE TABLE "TMStopModel" ("uid" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "relais_id" INTEGER NOT NULL, "mess_id" INTEGER)'
        sqlStatementSwitch = 'CREATE TABLE "TMSwitchModel" (""uid" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, relais_id" TEXT NOT NULL, "switchType" INTEGER)'
        cursor.execute(sqlStatementStop)
        cursor.execute(sqlStatementSwitch)
        connection.commit()
        connection.close()

    def insertStopModel(self, relaisId, messId):
        if self.openDatabase():
            # Insert a row of data
            self.curs.execute("INSERT INTO TMStopModel VALUES ('','')")
            self.conn.commit()
            self.conn.close()


    
        