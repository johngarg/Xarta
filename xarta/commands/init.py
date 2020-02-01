"""The init command."""


import os
from .base import BaseCommand
from ..database import initialise_database
from ..utils import XartaError, write_database_path


class Init(BaseCommand):
    """ Initialise database """

    def run(self):
        """Initialises a database and updates the database location in the config
        file."""

        database_location = self.options["<database-location>"]

        # resolve relative paths, e.g., 'xarta init ./'
        database_location = os.path.abspath(database_location)

        # verify folder exists
        if not os.path.isdir(database_location):
            raise XartaError("Directory does not exist.")

        # create xarta directory
        database_location = os.path.join(database_location, ".xarta.d")
        os.makedirs(database_location, exist_ok=True)
        database_path = os.path.join(database_location, "db.sqlite3")

        # initialise database
        initialise_database(database_path)

        # next update database location.
        write_database_path(database_path)
