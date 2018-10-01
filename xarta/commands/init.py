"""The init command."""


from .base import Base
from ..database import PaperDatabase

class Init(Base):
    """ Initialise database """

    def run(self):
        import os

        database_location = self.options['<database-location>'] + ".xarta.d/"
        database_path = database_location + "db.sqlite3"
        os.makedirs(database_location, exist_ok=True)

        # TODO Write some code to allow reinit of database to different location
        # and update of .xarta file accordingly

        if 'db.sqlite3' not in os.listdir(database_location):
            sql_command = "sqlite3 " + database_path + ' ";"'
            os.system(sql_command)
            paper_database = PaperDatabase(database_path)
            paper_database.create_connection()
            paper_database.initialise_database()
        else:
            print(database_path + " already exists.")
