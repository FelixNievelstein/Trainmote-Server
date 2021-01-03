import sqlite3
import os
import uuid

from .models.ConfigModel import ConfigModel
from .configControllerModule import ConfigController
from .models.GPIORelaisModel import GPIOSwitchPoint
from .models.GPIORelaisModel import GPIOStoppingPoint
from typing import Optional
from pkg_resources import parse_version


class DatabaseController():
    curs = None
    conn = None

    def checkUpdate(self, currentVersion: str):
        dbVersion = self.getVersion()
        if dbVersion is not None and parse_version(dbVersion) < parse_version("0.3.81"):
            self.setVersion("0.3.81")

    def openDatabase(self):
        config = ConfigController()
        dbPath = config.getDataBasePath()
        if dbPath is not None:
            print(dbPath)
            if not os.path.exists(dbPath):
                self.createInitalDatabse(dbPath)

            try:
                self.conn = sqlite3.connect(dbPath)
                self.curs = self.conn.cursor()
                return True
            except Exception as e:
                print(e)
                print('Error connecting database')
        return False

    def checkTableExists(self, name: str) -> bool:
        tableExists = False
        if self.openDatabase():
            def checkTable(lastrowid):
                nonlocal tableExists
                tableExists = self.curs.rowcount > 0

            self.execute("SELECT * FROM sqlite_master WHERE name ='%s' and type='table';" % (name), checkTable)
        return tableExists

    def createInitalDatabse(self, dbPath):
        connection = sqlite3.connect(dbPath)
        cursor = connection.cursor()
        sqlStatementStop = 'CREATE TABLE "TMStopModel" ("pk" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "uid" TEXT NOT NULL UNIQUE, "relais_id" INTEGER NOT NULL, "mess_id" INTEGER, "name" TEXT DEFAULT " ", "description" TEXT DEFAULT " ", "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
        sqlStatementSwitch = 'CREATE TABLE "TMSwitchModel" ("pk" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "uid" TEXT NOT NULL UNIQUE, "relais_id" INTEGER NOT NULL, "switchType" TEXT, "defaultValue" INTEGER, "needsPowerOn" INTEGER, "name" TEXT DEFAULT " ", "description" TEXT DEFAULT " ", "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
        sqlStatementVersion = 'CREATE TABLE "TMVersion" ("pk" INTEGER PRIMARY KEY CHECK (pk = 0), "version" TEXT NOT NULL)'
        sqlStatementConfig = 'CREATE TABLE "TMConfigModel" (pk INTEGER PRIMARY KEY CHECK (pk = 0), "switchPowerRelais" INTEGER, "powerRelais" INTEGER, "stateRelais" INTEGER, "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
        cursor.execute(sqlStatementStop)
        cursor.execute(sqlStatementSwitch)
        cursor.execute(sqlStatementVersion)
        cursor.execute(sqlStatementConfig)
        connection.commit()
        connection.close()

    def removeAll(self):
        if self.openDatabase():
            self.curs.execute("DELETE FROM TMSwitchModel")
            self.curs.execute("DELETE FROM TMStopModel")
            self.conn.commit()
            self.conn.close()

    def createUpdateStringFor(self, table: str, model, condition: Optional[str]) -> Optional[str]:
        string = "UPDATE %s SET " % (table)
        count = 0
        for property, value in vars(model).items():
            if property != "uid" and value is not None:
                if count == 0:
                    string = "%s %s = '%s' " % (string, property, value)
                else:
                    string = "%s, %s = '%s' " % (string, property, value)
                count = count + 1
        if condition is not None:
            string = "%s WHERE %s" % (string, condition)
        if count > 0:
            return string
        return None

##
# Version
##

    def setVersion(self, version: str):
        if self.openDatabase():
            self.execute("INSERT OR REPLACE INTO TMVersion(pk, version) VALUES ('0', '%s')" % (version), None)

    def getVersion(self) -> Optional[str]:
        version = None
        if self.openDatabase():
            def getVersionDB(lastrowid):
                nonlocal version
                for dataSet in self.curs:
                    version = dataSet[1]
            self.execute("SELECT * FROM TMVersion WHERE pk = '0';", getVersionDB)
        return version

##
# Configuration
##

    def getConfig(self) -> Optional[ConfigModel]:
        config = None
        if self.openDatabase():
            def getConfigDB(lastrowid):
                nonlocal config
                for dataSet in self.curs:
                    config = ConfigModel(dataSet[0], dataSet[1], dataSet[2], dataSet[3])
            self.execute("SELECT * FROM TMConfigModel WHERE pk = '0';", getConfigDB)
        return config

    def insertConfig(self, switchPowerRelais: int, powerRelais: int, stateRelais: int):
        if self.openDatabase():
            self.execute(
                "INSERT OR REPLACE INTO TMConfigModel(pk, switchPowerRelais, powerRelais, stateRelais) VALUES ('0', '%i','%i', '%i')"
                % (switchPowerRelais, powerRelais, stateRelais), None
            )

##
# Switch
##

    def insertSwitchModel(
        self,
        pin: int,
        switchType: str,
        needsPowerOn: bool,
        defaultValue: int,
        name: Optional[str],
        description: Optional[str]
    ) -> Optional[str]:
        switchUuid = None
        if self.openDatabase():
            intVal = 0
            if needsPowerOn:
                intVal = 1
            switchUuid = str(uuid.uuid4())

            # Insert a row of data
            def createdSwitch(uid):
                print(uid)

            self.execute(
                "INSERT INTO TMSwitchModel(uid, relais_id, switchType, defaultValue, needsPowerOn, name, description) VALUES ('%s', '%i', '%s', '%i', '%i', '%s', '%s')"
                % (switchUuid, pin, switchType, defaultValue, intVal, name, description), createdSwitch
            )

        return switchUuid

    def deleteSwitchModel(self, id: str):
        if self.openDatabase():
            # Insert a row of data
            self.execute("DELETE FROM TMSwitchModel WHERE uid = '%s';" % (id), None)

    def getSwitch(self, uid: str) -> Optional[GPIOSwitchPoint]:
        switch = None
        if self.openDatabase():
            def readSwitch(lastrowid):
                nonlocal switch
                for dataSet in self.curs:
                    switch = GPIOSwitchPoint(dataSet[1], dataSet[3], dataSet[2], dataSet[5], dataSet[6], dataSet[7])
                    switch.setDefaultValue(dataSet[4])

            self.execute("SELECT * FROM TMSwitchModel WHERE uid = '%s';" % (uid), readSwitch)

        return switch

    def updateSwitch(self, uid: str, updatModel: GPIOSwitchPoint) -> Optional[GPIOSwitchPoint]:
        updateString = self.createUpdateStringFor("TMSwitchModel", updatModel, "uid = %s" % (uid))
        if self.openDatabase() and updateString is not None:
            self.execute(updateString, None)
        return self.getSwitch(uid)

    def getAllSwichtModels(self):
        allSwitchModels = []
        if self.openDatabase():
            def readSwitchs(lastrowid):
                nonlocal allSwitchModels
                for dataSet in self.curs:
                    switchModel = GPIOSwitchPoint(dataSet[1], dataSet[3], dataSet[2], dataSet[5], dataSet[6], dataSet[7])
                    switchModel.setDefaultValue(dataSet[4])
                    allSwitchModels.append(switchModel)

            self.execute("SELECT * FROM TMSwitchModel", readSwitchs)

        return allSwitchModels

##
# Stops
##
    def getStop(self, uid: str) -> Optional[GPIOStoppingPoint]:
        stop = None
        if self.openDatabase():
            def readStop(lastrowid):
                nonlocal stop
                for dataSet in self.curs:
                    stop = GPIOStoppingPoint(dataSet[1], dataSet[2], dataSet[3], dataSet[4], dataSet[5])

            self.execute("SELECT * FROM TMStopModel WHERE uid = '%s';" % (uid), readStop)

        return stop

    def getAllStopModels(self):
        allStopModels = []
        if self.openDatabase():
            def readStops(lastrowid):
                nonlocal allStopModels
                for dataSet in self.curs:
                    stop = GPIOStoppingPoint(dataSet[1], dataSet[2], dataSet[3], dataSet[4], dataSet[5])
                    allStopModels.append(stop)

            self.execute("SELECT * FROM TMStopModel", readStops)

        return allStopModels

    def insertStopModel(
        self,
        relaisId: int,
        messId: Optional[int],
        name: Optional[str],
        description: Optional[str]
    ) -> Optional[str]:
        stopUuid = None
        if self.openDatabase():
            stopUuid = str(uuid.uuid4())

            # Insert a row of data
            def createdStop(uid):
                print(uid)

            if messId is not None:
                self.execute(
                    "INSERT INTO TMStopModel(uid, relais_id, mess_id, name, description) VALUES ('%s', '%i','%i', '%s', '%s')"
                    % (stopUuid, relaisId, messId, name, description), createdStop
                )
            else:
                self.execute(
                    "INSERT INTO TMStopModel(uid, relais_id, name, description) VALUES ('%s', '%i', '%s', '%s')"
                    % (stopUuid, relaisId, name, description), createdStop
                )
        return stopUuid

    def updateStop(self, uid: str, updatModel: GPIOStoppingPoint) -> Optional[GPIOStoppingPoint]:
        updateString = self.createUpdateStringFor("TMStopModel", updatModel, "uid = %s" % (uid))
        if self.openDatabase() and updateString is not None:
            self.execute(updateString, None)
        return self.getStop(uid)

    def deleteStopModel(self, id: str):
        if self.openDatabase():
            # Insert a row of data
            self.execute("DELETE FROM TMStopModel WHERE uid = '%s';" % (id), None)

    def execute(self, query, _callback):
        try:
            print(query)
            self.curs.execute(query)
            if _callback is not None:
                _callback(self.curs.lastrowid)
            self.conn.commit()
        except Exception as err:
            print('Query Failed: %s\nError: %s' % (query, str(err)))
        finally:
            self.conn.close()
            self.curs = None
            self.conn = None
