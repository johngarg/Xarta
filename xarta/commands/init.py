"""The init command."""


import os
from .base import BaseCommand
from ..database import initialise_database
from ..utils import XartaError, write_config, CONFIG_FILE


class Init(BaseCommand):
    """ Initialise database """

    def run(self):
        """Initialises a database and updates the database location in the config
        file."""

        database_file = self.options["<database-file>"]

        if database_file is None:
            # default to writing to same directoy as CONFIG_FILE
            database_location = os.path.dirname(CONFIG_FILE)

            fn = "xarta.db"
            # if the config file starts with a '.', so will the database file.
            if os.path.basename(CONFIG_FILE)[0] == ".":
                fn = "." + fn

            database_file = os.path.join(database_location, fn)

        else:
            # resolve relative paths, e.g., 'xarta init ./'
            database_location = os.path.abspath(database_location)
            database_location = os.path.dirname(database_file)

        os.makedirs(database_location, exist_ok=True)

        # initialise database
        initialise_database(database_file)

        # next update database location.
        write_config({"database_file": database_file})
