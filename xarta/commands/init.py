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

        database_location = self.options["<database-file>"]

        # resolve relative paths, e.g., 'xarta init ./'
        database_location = os.path.abspath(database_location)

        # verify base folder exists
        if not os.path.isdir(os.path.dirname(database_location)):
            raise XartaError(
                "Directory does not exist: " + str(os.path.dirname(database_location))
            )

        # create xarta directory
        database_path = os.path.join(database_location, "xarta.db")

        # initialise database
        initialise_database(database_path)

        # next update database location.
        write_database_path(database_path)
