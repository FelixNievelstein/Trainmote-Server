
class LibInstaller():

    def installSQLite(self):
        print('Installation SQLite')
        from subprocess import call
        call('sudo apt-get install sqlite3', shell=True)
