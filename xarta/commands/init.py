"""The init command."""


from .base import Base
from ..database import initialise_database, write_database_location


class Init(Base):
    """ Initialise database """

    def run(self):
        import os

        database_location = self.options["<database-location>"]

        # resolve relative paths, e.g., 'xarta init ./'
        database_location = os.path.abspath(database_location)

        # verify folder exists
        if not os.path.isdir(database_location):
            raise Exception("Directory does not exist.")

        # create xarta directory
        database_location += "/.xarta.d"
        os.makedirs(database_location, exist_ok=True)
        database_path = database_location + "/db.sqlite3"

        if "db.sqlite3" not in os.listdir(database_location):
            initialise_database(database_path)
            write_database_location(database_path)
        else:
            print(database_path + " already exists.")
            write_database_location(database_path)
