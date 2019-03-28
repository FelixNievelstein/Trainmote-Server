import sqlite3

class DatabaseController():
    def __init__(self):
        print('Init Database Controller')

        ############### Settings ####################
        #DB Name
        DB_NAME = "TrainmoteDB"

        #SQL File with Table Schema and Initialization Data
        SQL_File_Name = "content/tom-db.sqlite"
        ##############################################

        #Read Table Schema into a Variable and remove all New Line Chars
        TableSchema=""
        with open(SQL_File_Name, 'r') as SchemaFile:
            TableSchema = SchemaFile.read().replace('\n')

        #Connect or Create DB File
        conn = sqlite3.connect(DB_NAME)
        curs = conn.cursor()

        #Create Tables
        sqlite3.complete_statement(TableSchema)
        curs.executescript(TableSchema)

        #Close DB
        curs.close()
        conn.close()