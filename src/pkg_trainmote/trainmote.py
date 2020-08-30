from . import gpioservice
from .powerControllerModule import PowerThread
from .configControllerModule import ConfigController
from . import stateControllerModule
from .libInstaller import LibInstaller
from subprocess import call
import logging
import logging.handlers
import argparse
import sys
import os
import time

gpioservice.setup()
gpioservice.loadInitialData()
stateController = stateControllerModule.StateController()
powerThread = PowerThread()
client_sock = None
config = ConfigController()  

def loadPersistentData():
    if config.loadPreferences():
        if not config.isSQLiteInstalled():
            libInstaller = LibInstaller()
            libInstaller.installSQLite()
            if config.setSQLiteInstalled():
                restart(None, None)
            else: 
                shutDown(None)

# Main loop
def main():          
    powerThread.start()
    loadPersistentData()


def restart(server_sock, client_sock):
    closeClientConnection(client_sock)
    shutDown(server_sock)
    os.execv(sys.executable, ['python'] + sys.argv)

def shutDown(server_sock):
    powerThread.kill.set()
    powerThread.isTurningOff = True
    powerThread.join()
    stateController.setState(stateControllerModule.STATE_SHUTDOWN)
    if server_sock is not None:
        server_sock.close()
    print ("Server going down")
    stateController.stop()

def closeClientConnection(client_sock):
    print ("Closing client socket")
    if client_sock is not None:
            client_sock.close()
            client_sock = None

if __name__ == '__main__':
    main()