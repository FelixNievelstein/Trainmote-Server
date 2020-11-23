from typing import Optional
from . import apiController
import os
import argparse


version: str = '0.3.96'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--autostart", help="sets trainmote to start on every device boot.", action="store_true")
    args = parser.parse_args()
    if args.autostart:
        print("write to rc.local")
        setAutoStart()
    apiController.setup(version)


def setAutoStart():
    lineToAdd = 'sudo trainmote &\n'

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


if __name__ == '__main__':
    main()
