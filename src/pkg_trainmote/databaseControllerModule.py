import sqlite3
import os
from .configControllerModule import ConfigController
from .models.GPIORelaisModel import GPIOSwitchPoint
from .models.GPIORelaisModel import GPIOStoppingPoint


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
        sqlStatementSwitch = 'CREATE TABLE "TMSwitchModel" ("uid" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "relais_id" INTEGER NOT NULL, "switchType" TEXT, "defaultValue" INTEGER)'
        cursor.execute(sqlStatementStop)
        cursor.execute(sqlStatementSwitch)
        connection.commit()
        connection.close()

    def insertStopModel(self, relaisId, messId):
        if self.openDatabase():
            # Insert a row of data
            if messId is not None:
                self.execute("INSERT INTO TMStopModel(relais_id, mess_id) VALUES ('%i','%i')" % (relaisId, messId), None)
            else:
                self.execute("INSERT INTO TMStopModel(relais_id) VALUES ('%i')" % (relaisId), None)

    def insertSwitchModel(self, model):
        if self.openDatabase():
            # Insert a row of data
            self.execute("INSERT INTO TMSwitchModel(relais_id, switchType, defaultValue) VALUES ('%i','%s', '%i')" % (model.pin, model.switchType, model.defaultValue), None)

    def removeAll(self):
        if self.openDatabase():
            self.curs.execute("DELETE FROM TMSwitchModel")
            self.curs.execute("DELETE FROM TMStopModel")
            self.conn.commit()
            self.conn.close()

    def getAllSwichtModels(self):
        allSwitchModels = []
        if self.openDatabase():
            def readSwitchs():
                nonlocal allSwitchModels
                for dataSet in self.curs:
                    switchModel = GPIOSwitchPoint(dataSet[1], dataSet[2], dataSet[1])
                    switchModel.setDefaultValue(dataSet[3])
                    allSwitchModels.append(switchModel)

            self.execute("SELECT * FROM TMSwitchModel", readSwitchs)

        return allSwitchModels

    def getAllStopModels(self):
        allStopModels = []
        if self.openDatabase():
            def readStops():
                nonlocal allStopModels
                for dataSet in self.curs:
                    stop = GPIOStoppingPoint(dataSet[1], dataSet[1], dataSet[2])
                    allStopModels.append(stop)

            self.execute("SELECT * FROM TMStopModel", readStops)

        return allStopModels

    def execute(self, query, _callback):
        try:
            print(query)
            self.curs.execute(query)
            if _callback is not None:
                _callback()
            self.conn.commit()
        except Exception as err:
            print('Query Failed: %s\nError: %s' % (query, str(err)))
        finally:
            self.conn.close()
            self.curs = None
            self.conn = None
