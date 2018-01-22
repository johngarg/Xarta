"""The init command."""


from .base import Base
from ..database import create_connection, initialise_database

class Init(Base):
    """ Initialise database """

    def run(self):
        import sqlite3
        import os

        database_location = self.options['<database-location>'] + '.xarta.d/'
        database_path = database_location + 'db.sqlite3'
        os.makedirs(database_location, exist_ok=True)

        # TODO Write some code to allow reinit of database to different location and update of .xarta file accordingly

        if 'db.sqlite3' not in os.listdir(database_location):
            sql_command = 'sqlite3 ' + database_path + ' ";"'
            os.system(sql_command)
            create_connection(database_path)
            initialise_database(database_path)
        else:
            print(database_path + ' already exists.')
