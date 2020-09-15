import sqlite3
import os
from .configControllerModule import ConfigController
from .models.GPIORelaisModel import GPIOSwitchPoint
from .models.GPIORelaisModel import GPIOStoppingPoint
from typing import Optional


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

    def insertStopModel(self, relaisId: int, messId: Optional[int]) -> Optional[int]:
        resultUid = None
        if self.openDatabase():
            # Insert a row of data
            def createdStop(uid):
                nonlocal resultUid
                resultUid = uid

            if messId is not None:
                self.execute("INSERT INTO TMStopModel(relais_id, mess_id) VALUES ('%i','%i')" % (relaisId, messId), createdStop)
            else:
                self.execute("INSERT INTO TMStopModel(relais_id) VALUES ('%i')" % (relaisId), createdStop)
        return resultUid

    def deleteStopModel(self, id: int):
        if self.openDatabase():
            # Insert a row of data
            self.execute("DELETE FROM TMStopModel WHERE uid = '%i';" % (id), None)

    def insertSwitchModel(self, pin: int, switchType: str, defaultValue: int) -> Optional[int]:
        resultUid = None
        if self.openDatabase():
            # Insert a row of data
            def createdSwitch(uid):
                nonlocal resultUid
                resultUid = uid
            self.execute("INSERT INTO TMSwitchModel(relais_id, switchType, defaultValue) VALUES ('%i','%s', '%i')" % (pin, switchType, defaultValue), createdSwitch)

        return resultUid

    def deleteSwitchModel(self, id: int):
        if self.openDatabase():
            # Insert a row of data
            self.execute("DELETE FROM TMSwitchModel WHERE uid = '%i';" % (id), None)

    def removeAll(self):
        if self.openDatabase():
            self.curs.execute("DELETE FROM TMSwitchModel")
            self.curs.execute("DELETE FROM TMStopModel")
            self.conn.commit()
            self.conn.close()

    def getSwitch(self, uid) -> Optional[GPIOSwitchPoint]:
        switch = None
        if self.openDatabase():
            def readSwitch(lastrowid):
                nonlocal switch
                for dataSet in self.curs:
                    switch = GPIOSwitchPoint(dataSet[0], dataSet[2], dataSet[1])

            self.execute("SELECT * FROM TMSwitchModel WHERE uid = '%i';" % (uid), readSwitch)

        return switch

    def getAllSwichtModels(self):
        allSwitchModels = []
        if self.openDatabase():
            def readSwitchs(lastrowid):
                nonlocal allSwitchModels
                for dataSet in self.curs:
                    switchModel = GPIOSwitchPoint(dataSet[0], dataSet[2], dataSet[1])
                    switchModel.setDefaultValue(dataSet[3])
                    allSwitchModels.append(switchModel)

            self.execute("SELECT * FROM TMSwitchModel", readSwitchs)

        return allSwitchModels

    def getStop(self, uid) -> Optional[GPIOStoppingPoint]:
        switch = None
        if self.openDatabase():
            def readSwitch(lastrowid):
                nonlocal switch
                for dataSet in self.curs:
                    switch = GPIOStoppingPoint(dataSet[0], dataSet[1], dataSet[2])

            self.execute("SELECT * FROM TMStopModel WHERE uid = '%i';" % (uid), readSwitch)

        return switch

    def getAllStopModels(self):
        allStopModels = []
        if self.openDatabase():
            def readStops(lastrowid):
                nonlocal allStopModels
                for dataSet in self.curs:
                    stop = GPIOStoppingPoint(dataSet[0], dataSet[1], dataSet[2])
                    allStopModels.append(stop)

            self.execute("SELECT * FROM TMStopModel", readStops)

        return allStopModels

    def execute(self, query, _callback):
        try:
            print(query)
            self.curs.execute(query)
            print(self.curs.lastrowid)
            if _callback is not None:
                _callback(self.curs.lastrowid)
            self.conn.commit()
        except Exception as err:
            print('Query Failed: %s\nError: %s' % (query, str(err)))
        finally:
            self.conn.close()
            self.curs = None
            self.conn = None
