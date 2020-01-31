"""The init command."""


from .base import BaseCommand
from ..database import initialise_database


class Init(BaseCommand):
    """ Initialise database """

    def run(self):
        initialise_database(self.options["<database-location>"])
