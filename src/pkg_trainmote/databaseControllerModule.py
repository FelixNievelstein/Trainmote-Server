import sqlite3
import os

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
        sqlStatementStop = 'CREATE TABLE "TMStopModel" ("uid" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "relais_id" INTEGER NOT NULL, "mess_id" INTEGER, "name" TEXT DEFAULT " ", "description" TEXT DEFAULT " ", "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
        sqlStatementSwitch = 'CREATE TABLE "TMSwitchModel" ("uid" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "relais_id" INTEGER NOT NULL, "switchType" TEXT, "defaultValue" INTEGER, "name" TEXT DEFAULT " ", "description" TEXT DEFAULT " ", "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
        sqlStatementVersion = 'CREATE TABLE "TMVersion" ("uid" INTEGER PRIMARY KEY CHECK (uid = 0), "version" TEXT NOT NULL)'
        sqlStatementConfig = 'CREATE TABLE "TMConfigModel" (uid INTEGER PRIMARY KEY CHECK (uid = 0), "switchPowerRelais" INTEGER, "powerRelais" INTEGER, "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
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

##
# Version
##

    def setVersion(self, version: str):
        if self.openDatabase():
            self.execute("INSERT OR REPLACE INTO TMVersion(uid, version) VALUES ('0', '%s')" % (version), None)

    def getVersion(self) -> Optional[str]:
        version = None
        if self.openDatabase():
            def getVersionDB(lastrowid):
                nonlocal version
                for dataSet in self.curs:
                    version = dataSet[1]
            self.execute("SELECT * FROM TMVersion WHERE uid = '0';", getVersionDB)
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
                    config = ConfigModel(dataSet[0], dataSet[1], dataSet[2])
            self.execute("SELECT * FROM TMConfigModel WHERE uid = '0';", getConfigDB)
        return config

    def insertConfig(self, switchPowerRelais: int, powerRelais: int):
        if self.openDatabase():
            self.execute(
                "INSERT OR REPLACE INTO TMConfigModel(uid, switchPowerRelais, powerRelais) VALUES ('0', '%i','%i')"
                % (switchPowerRelais, powerRelais), None
            )

##
# Switch
##

    def insertSwitchModel(
        self,
        pin: int,
        switchType: str,
        defaultValue: int,
        name: Optional[str],
        description: Optional[str]
    ) -> Optional[int]:
        resultUid = None
        if self.openDatabase():
            # Insert a row of data
            def createdSwitch(uid):
                nonlocal resultUid
                resultUid = uid
            self.execute(
                "INSERT INTO TMSwitchModel(relais_id, switchType, defaultValue, name, description) VALUES ('%i', '%s', '%i', '%s', '%s')"
                % (pin, switchType, defaultValue, name, description), createdSwitch
            )

        return resultUid

    def deleteSwitchModel(self, id: int):
        if self.openDatabase():
            # Insert a row of data
            self.execute("DELETE FROM TMSwitchModel WHERE uid = '%i';" % (id), None)

    def getSwitch(self, uid) -> Optional[GPIOSwitchPoint]:
        switch = None
        if self.openDatabase():
            def readSwitch(lastrowid):
                nonlocal switch
                for dataSet in self.curs:
                    switch = GPIOSwitchPoint(dataSet[0], dataSet[2], dataSet[1], dataSet[4], dataSet[5])
                    switch.setDefaultValue(dataSet[3])

            self.execute("SELECT * FROM TMSwitchModel WHERE uid = '%i';" % (uid), readSwitch)

        return switch

    def getAllSwichtModels(self):
        allSwitchModels = []
        if self.openDatabase():
            def readSwitchs(lastrowid):
                nonlocal allSwitchModels
                for dataSet in self.curs:
                    switchModel = GPIOSwitchPoint(dataSet[0], dataSet[2], dataSet[1], dataSet[4], dataSet[5])
                    switchModel.setDefaultValue(dataSet[3])
                    allSwitchModels.append(switchModel)

            self.execute("SELECT * FROM TMSwitchModel", readSwitchs)

        return allSwitchModels

##
# Stops
##
    def getStop(self, uid) -> Optional[GPIOStoppingPoint]:
        stop = None
        if self.openDatabase():
            def readStop(lastrowid):
                nonlocal stop
                for dataSet in self.curs:
                    stop = GPIOStoppingPoint(dataSet[0], dataSet[1], dataSet[2], dataSet[3], dataSet[4])

            self.execute("SELECT * FROM TMStopModel WHERE uid = '%i';" % (uid), readStop)

        return stop

    def getAllStopModels(self):
        allStopModels = []
        if self.openDatabase():
            def readStops(lastrowid):
                nonlocal allStopModels
                for dataSet in self.curs:
                    stop = GPIOStoppingPoint(dataSet[0], dataSet[1], dataSet[2], dataSet[3], dataSet[4])
                    allStopModels.append(stop)

            self.execute("SELECT * FROM TMStopModel", readStops)

        return allStopModels

    def insertStopModel(
        self,
        relaisId: int,
        messId: Optional[int],
        name: Optional[str],
        description: Optional[str]
    ) -> Optional[int]:
        resultUid = None
        if self.openDatabase():
            # Insert a row of data
            def createdStop(uid):
                nonlocal resultUid
                resultUid = uid

            if messId is not None:
                self.execute(
                    "INSERT INTO TMStopModel(relais_id, mess_id, name, description) VALUES ('%i','%i', '%s', '%s')"
                    % (relaisId, messId, name, description), createdStop
                )
            else:
                self.execute(
                    "INSERT INTO TMStopModel(relais_id, name, description) VALUES ('%i', '%s', '%s')"
                    % (relaisId, name, description), createdStop
                )
        return resultUid

    def deleteStopModel(self, id: int):
        if self.openDatabase():
            # Insert a row of data
            self.execute("DELETE FROM TMStopModel WHERE uid = '%i';" % (id), None)

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
