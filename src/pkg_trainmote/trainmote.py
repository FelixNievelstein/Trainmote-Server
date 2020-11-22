from typing import Optional
from . import apiController
import sys
import argparse

version: str = '0.3.94'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "-autostart", help="sets trainmote to start on every device boot.", action="store_true")
    args = parser.parse_args()
    if args.autostart:
        print("write to rc.local")
    apiController.setup(version)

if __name__ == '__main__':
    main()
