import sqlite3

class DatabaseController():
    def __init__(self):
        print('Connect Database Controller')
        try:
            conn = sqlite3.connect('content/tom-db.sqlite')
            curs = conn.cursor()
        except:
            print('Error connecting database')
        