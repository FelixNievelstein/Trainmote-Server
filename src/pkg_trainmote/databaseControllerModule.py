import sqlite3
import os
from sqlite3.dbapi2 import DataError
import uuid
import json

from .models.ConfigModel import ConfigModel
from .configControllerModule import ConfigController
from .models.GPIORelaisModel import GPIOSwitchPoint
from .models.GPIORelaisModel import GPIOStoppingPoint
from .models.Program import Program
from .models.Action import Action
from typing import Optional, List, Any
from pkg_resources import parse_version
from .models.User import User
from werkzeug.security import generate_password_hash


class DatabaseController():
    curs = None
    conn = None

    def checkUpdate(self, currentVersion: str):
        dbVersion = self.getVersion()
        if dbVersion is not None and parse_version(dbVersion) < parse_version("0.3.81"):
            self.setVersion("0.3.81")
        if dbVersion is None or dbVersion is not None and parse_version(dbVersion) < parse_version("0.5.0"):
            self.updateDatabase_0_5_0()
            self.setVersion(currentVersion)

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
        sqlStatementStop = 'CREATE TABLE "TMStopModel" ("pk" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "uid" TEXT NOT NULL UNIQUE, "relais_id" INTEGER NOT NULL, "mess_id" INTEGER, "defaultValue" INTEGER, "name" TEXT DEFAULT " ", "description" TEXT DEFAULT " ", "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
        sqlStatementSwitch = 'CREATE TABLE "TMSwitchModel" ("pk" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "uid" TEXT NOT NULL UNIQUE, "relais_id" INTEGER NOT NULL, "switchType" TEXT, "defaultValue" INTEGER, "needsPowerOn" INTEGER, "name" TEXT DEFAULT " ", "description" TEXT DEFAULT " ", "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
        sqlStatementVersion = 'CREATE TABLE "TMVersion" ("pk" INTEGER PRIMARY KEY CHECK (pk = 0), "version" TEXT NOT NULL)'
        sqlStatementConfig = 'CREATE TABLE "TMConfigModel" (pk INTEGER PRIMARY KEY CHECK (pk = 0), "switchPowerRelais" INTEGER, "powerRelais" INTEGER, "stateRelais" INTEGER, "deviceName" TEXT, "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
        sqlStatementUser = 'CREATE TABLE "TMUser" ("pk" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "uid" TEXT NOT NULL UNIQUE, "username" TEXT NOT NULL UNIQUE, "password" TEXT NOT NULL, "roles" TEXT NOT NULL, "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
        cursor.execute(sqlStatementStop)
        cursor.execute(sqlStatementSwitch)
        cursor.execute(sqlStatementVersion)
        cursor.execute(sqlStatementConfig)
        cursor.execute(sqlStatementUser)
        connection.commit()
        connection.close()

    def updateDatabase_0_5_0(self):
        if self.openDatabase():
            programTable = 'CREATE TABLE "TMProgramModel" ("pk" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "uid" TEXT NOT NULL UNIQUE, "name" TEXT, "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
            actionTable = 'CREATE TABLE "TMActionModel" ("pk" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "uid" TEXT NOT NULL UNIQUE, "program" INTEGER NOT NULL, "type" TEXT NOT NULL, "position" INTEGER NOT NULL, "inputs" TEXT NOT NULL, "name" TEXT, "updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, "created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)'
            self.curs.execute(programTable)
            self.curs.execute(actionTable)
            self.conn.commit()
            self.conn.close()

    def removeAll(self):
        if self.openDatabase():
            self.curs.execute("DELETE FROM TMSwitchModel")
            self.curs.execute("DELETE FROM TMStopModel")
            self.conn.commit()
            self.conn.close()

    def createUpdateStringFor(self, table: str, model, condition: Optional[str], encoder = None) -> Optional[str]:
        string = "UPDATE %s SET " % (table)
        count = 0
        for property, value in vars(model).items():
            if property != "uid" and value is not None:
                if encoder is not None:
                    mValue = encoder(property, value)
                    if count == 0:
                        string = "%s %s = '%s' " % (string, property, mValue)
                    else:
                        string = "%s, %s = '%s' " % (string, property, mValue)
                else:
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
                    config = ConfigModel(dataSet[0], dataSet[1], dataSet[2], dataSet[3], dataSet[4])
            self.execute("SELECT * FROM TMConfigModel WHERE pk = '0';", getConfigDB)
        return config

    def insertConfig(
        self,
        switchPowerRelais: Optional[int],
        powerRelais: Optional[int],
        stateRelais: Optional[int],
        deviceName: Optional[str]
    ):
        if self.openDatabase():
            if powerRelais is None:
                powerRelais = 0

            if switchPowerRelais is None:
                switchPowerRelais = 0

            if stateRelais is None:
                stateRelais = 0

            self.execute(
                "INSERT OR REPLACE INTO TMConfigModel(pk, switchPowerRelais, powerRelais, stateRelais, deviceName) VALUES ('0', '%i','%i', '%i', '%s')"
                % (switchPowerRelais, powerRelais, stateRelais, deviceName), None
            )

##
# User
##

    def getUser(self, name: str) -> Optional[User]:
        user = None
        if self.openDatabase():
            def getUserDB(lastrowid):
                nonlocal user
                for dataSet in self.curs:
                    user = User(dataSet[1], dataSet[2], dataSet[3], dataSet[4])
            self.execute("SELECT * FROM TMUser WHERE username = '%s';" % (name), getUserDB)
        return user

    def getUsers(self) -> List[User]:
        users: List[User] = []
        if self.openDatabase():
            def usersLoaded(lastrowid):
                nonlocal users
                for dataSet in self.curs:
                    users.append(User(dataSet[1], dataSet[2], dataSet[3], dataSet[4]))
            self.execute("SELECT * FROM TMUser", usersLoaded)
        return users

    def insertUser(self, name: str, password: str, role: str):
        if self.openDatabase():
            userUuid = str(uuid.uuid4())

            def createUser(uid):
                print(uid)
            self.execute(
                "INSERT INTO TMUser(uid, username, password, roles) VALUES ('%s', '%s', '%s', '%s')"
                % (userUuid, name, generate_password_hash(password), role), createUser
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

    def getSwitchForDataSet(self, dataSet) -> GPIOSwitchPoint:
        needsPowerOn = True
        if dataSet[5] == 0:
            needsPowerOn = False
        switch = GPIOSwitchPoint(dataSet[1], dataSet[3], dataSet[2], needsPowerOn, dataSet[6], dataSet[7])
        switch.setDefaultValue(dataSet[4])
        return switch

    def getSwitch(self, uid: str) -> Optional[GPIOSwitchPoint]:
        switch = None
        if self.openDatabase():
            def readSwitch(lastrowid):
                nonlocal switch
                for dataSet in self.curs:
                    switch = self.getSwitchForDataSet(dataSet)

            self.execute("SELECT * FROM TMSwitchModel WHERE uid = '%s';" % (uid), readSwitch)

        return switch

    def updateSwitch(self, uid: str, updatModel: GPIOSwitchPoint) -> Optional[GPIOSwitchPoint]:
        updateString = self.createUpdateStringFor("TMSwitchModel", updatModel, "uid = '%s'" % (uid))
        if self.openDatabase() and updateString is not None:
            self.execute(updateString, None)
        return self.getSwitch(uid)

    def getAllSwichtModels(self):
        allSwitchModels = []
        if self.openDatabase():
            def readSwitchs(lastrowid):
                nonlocal allSwitchModels
                for dataSet in self.curs:
                    switchModel = self.getSwitchForDataSet(dataSet)
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
                    stop = self.getStopForDataSet(dataSet)

            self.execute("SELECT * FROM TMStopModel WHERE uid = '%s';" % (uid), readStop)

        return stop

    def getAllStopModels(self):
        allStopModels = []
        if self.openDatabase():
            def readStops(lastrowid):
                nonlocal allStopModels
                for dataSet in self.curs:
                    stop = self.getStopForDataSet(dataSet)
                    allStopModels.append(stop)

            self.execute("SELECT * FROM TMStopModel", readStops)

        return allStopModels

    def getStopForDataSet(self, dataSet) -> GPIOStoppingPoint:
        stop = GPIOStoppingPoint(dataSet[1], dataSet[2], dataSet[3], dataSet[5], dataSet[6])
        stop.setDefaultValue(dataSet[4])
        return stop

    def insertStopModel(
        self,
        relaisId: int,
        messId: Optional[int],
        name: Optional[str],
        defaultValue: int,
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
                    "INSERT INTO TMStopModel(uid, relais_id, mess_id, defaultValue, name, description) VALUES ('%s', '%i', '%i', '%i', '%s', '%s')"
                    % (stopUuid, relaisId, messId, defaultValue, name, description), createdStop
                )
            else:
                self.execute(
                    "INSERT INTO TMStopModel(uid, relais_id, defaultValue, name, description) VALUES ('%s', '%i', '%i', '%s', '%s')"
                    % (stopUuid, relaisId, defaultValue, name, description), createdStop
                )
        return stopUuid

    def updateStop(self, uid: str, updatModel: GPIOStoppingPoint) -> Optional[GPIOStoppingPoint]:
        updateString = self.createUpdateStringFor("TMStopModel", updatModel, "uid = '%s'" % (uid))
        if self.openDatabase() and updateString is not None:
            self.execute(updateString, None)
        return self.getStop(uid)

    def deleteStopModel(self, id: str):
        if self.openDatabase():
            # Insert a row of data
            self.execute("DELETE FROM TMStopModel WHERE uid = '%s';" % (id), None)

##
# Programs
##

    def insertProgram(self, name: Optional[str]) -> Optional[str]:
        progUuid = None
        if self.openDatabase():
            progUuid = str(uuid.uuid4())

            self.execute(
                "INSERT INTO TMProgramModel(uid, name) VALUES ('%s', '%s')" % (progUuid, name), None
            )
        return progUuid

    def getProgram(self, uid: str) -> Optional[Program]:
        program = None
        pk: Optional[int] = None
        if self.openDatabase():
            def readProgram(lastrowid):
                nonlocal program
                nonlocal pk
                dataSet = self.curs.fetchone()
                program = self.getProgramForDataSet(dataSet)
                pk = dataSet[0]

            self.execute("SELECT * FROM TMProgramModel WHERE uid = '%s';" % (uid), readProgram)

        if pk is not None and program is not None:
            program.actions = self.getActionsFor(pk) or []
        return program

    def getProgramPk(self, uid: str) -> Optional[int]:
        programPk = None
        if self.openDatabase():

            def readProgram(lastrowid):
                nonlocal programPk
                programPk = self.curs.fetchone()[0]

            self.execute("SELECT * FROM TMProgramModel WHERE uid = '%s';" % (uid), readProgram)

        return programPk

    def getAllPrograms(self):
        allProgramIds = []
        allPrograms = []
        if self.openDatabase():
            def readPrograms(lastrowid):
                nonlocal allPrograms
                for dataSet in self.curs:
                    allProgramIds.append(dataSet[1])

            self.execute("SELECT * FROM TMProgramModel", readPrograms)

        for id in allProgramIds:
            program = self.getProgram(id)
            allPrograms.append(program)

        return allPrograms

    def getProgramForDataSet(self, dataSet) -> Program:
        return Program(dataSet[1], [], dataSet[2])

    def deleteProgram(self, id: str):
        pk = self.getProgramPk(id)
        if pk is not None:
            actions = self.getActionsFor(pk)
            for action in actions:
                if action.uid is not None:
                    self.deleteAction(action.uid)

        if self.openDatabase():
            # Insert a row of data
            self.execute("DELETE FROM TMProgramModel WHERE uid = '%s';" % (id), None)

    def updateProgram(self, uid: str, updatModel: Program) -> Optional[Program]:
        programPk = self.getProgramPk(uid)
        if programPk is not None:
            for action in updatModel.actions:
                if action.uid is not None:
                    self.updateAction(action)
                else:
                    self.insertAction(action, programPk)
            if updatModel.name is not None and self.openDatabase():
                self.execute("UPDATE TMProgramModel SET name = '%s'  WHERE uid = '%s';" % (updatModel.name, uid), None)
        else:
            raise ValueError("Program not found")
        return self.getProgram(uid)
##
# Actions
##

    def insertAction(
        self,
        action: Action,
        programId: int
    ) -> Optional[str]:
        actionUuid = None
        if self.openDatabase():
            actionUuid = str(uuid.uuid4())
            if action.inputs is None:
                raise ValueError("No values found for action")
            inputsString = self.encodeValues(action.inputs)

            def createdProgram(uid):
                print(uid)

            self.executeWith(
                "INSERT INTO TMActionModel(uid, program, type, position, inputs, name) VALUES (?, ?, ?, ?, ?, ?)",
                createdProgram, (actionUuid, programId, action.type, action.position, inputsString, action.name)
            )
        return actionUuid

    def decodeValues(self, inputs: str) -> List[str]:
        return json.loads(inputs)

    def encodeValues(self, inputs: List[str]) -> str:
        return json.dumps(inputs)

    def getActionsFor(self, program: int) -> Optional[List[Action]]:
        allActions = []
        if self.openDatabase():
            def readActions(lastrowid):
                nonlocal allActions
                for dataSet in self.curs:
                    action = self.getActionForDataSet(dataSet)
                    allActions.append(action)

            self.execute("SELECT * FROM TMActionModel WHERE program = %i" % (program), readActions)
        allActions.sort(key=self.get_position)
        return allActions

    def get_position(self, action: Action) -> int:
        return action.position or 0

    def getAction(self, uid: str) -> Optional[Action]:
        action = None
        if self.openDatabase():
            def readAction(lastrowid):
                nonlocal action
                action = self.getActionForDataSet(self.curs.fetchone())

            self.execute("SELECT * FROM TMActionModel WHERE uid = '%s';" % (uid), readAction)

        return action

    def getActionForDataSet(self, dataSet) -> Action:
        return Action(dataSet[1], dataSet[3], dataSet[4], self.decodeValues(dataSet[5]), dataSet[6])

    def deleteAction(self, id: str):
        if self.openDatabase():
            self.execute("DELETE FROM TMActionModel WHERE uid = '%s';" % (id), None)

    def updateAction(self, updateModel: Action) -> Optional[Action]:
        if updateModel.uid is not None:
            def encode(propertyName, value) -> Any:
                if propertyName == "inputs":
                    return self.encodeValues(value)
                else:
                    return value

            updateString = self.createUpdateStringFor("TMActionModel", updateModel, "uid = '%s'" % (updateModel.uid), encode)
            if self.openDatabase() and updateString is not None:
                self.execute(updateString, None)
            return self.getAction(updateModel.uid)
        return None

    def execute(self, query, _callback, shouldClose: bool = True):
        try:
            print(query)
            self.curs.execute(query)
            if _callback is not None:
                _callback(self.curs.lastrowid)
            if shouldClose:
                self.conn.commit()
        except Exception as err:
            print('Query Failed: %s\nError: %s' % (query, str(err)))
        finally:
            if shouldClose:
                self.conn.close()
                self.curs = None
                self.conn = None

    def executeWith(self, query, _callback, parameters: Any):
        try:
            print(query)
            self.curs.execute(query, parameters)
            if _callback is not None:
                _callback(self.curs.lastrowid)
            self.conn.commit()
        except Exception as err:
            print('Query Failed: %s\nError: %s' % (query, str(err)))
        finally:
            self.conn.close()
            self.curs = None
            self.conn = None
