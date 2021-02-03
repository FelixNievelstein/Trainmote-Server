from pkg_trainmote.databaseControllerModule import DatabaseController
from . import apiController
import os
import argparse
from subprocess import call
from . import configControllerModule


version: str = '0.4.68'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--autostart",
        help="Adds trainmote to boot process. Please note that you need to use sudo for this option.",
        action="store_true"
    )
    args = parser.parse_args()
    if args.autostart:
        setAutoStart()

    database = DatabaseController()
    if not database.getUsers():
        print("!!!Welcome Trainmote.!!!")
        print("First you have to create a user for your Trainmote. Please write down the login details so that you can find them again at any time.")
        username = input("Enter username: ")
        password = setPassword()
        database.insertUser(username, password, "admin")

    apiController.setup(version)


def setAutoStart():
    contentDir = configControllerModule.ConfigController().getContentDir()
    lineToAdd = 'sudo trainmote & > ' + contentDir + '/log.txt 2>&1\n'

    try:
        with open('/etc/rc.local') as fin:
            with open('/etc/rc.local.TMP', 'w+') as fout:
                alreadyAdded = False
                for line in fin:
                    if line == lineToAdd:
                        alreadyAdded = True
                    if line.startswith('exit 0') and not alreadyAdded:
                        fout.write(lineToAdd)
                    fout.write(line)
                os.rename('/etc/rc.local', '/etc/rc.local.jic')
                os.rename('/etc/rc.local.TMP', '/etc/rc.local')
                call("sudo chmod +x /etc/rc.local", shell=True)
    except PermissionError:
        print("Autostart needs root permission")

def setPassword() -> str:
    password = input("Please enter a password: ")
    secondPassword = input("Please repeat the password: ")
    if password == secondPassword:
        return password
    else:
        print("The passwords do not match.")
        return setPassword()

if __name__ == '__main__':
    main()
