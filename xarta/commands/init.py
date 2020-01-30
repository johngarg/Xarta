"""The init command."""


from .base import Base
from ..database import initialise_database


class Init(Base):
    """ Initialise database """

    def run(self):
        database_location = self.options["<database-location>"]
        initialise_database(database_location)
