"""The init command."""


from .base import Base
from ..database import PaperDatabase


class Init(Base):
    """ Initialise database """

    def run(self):
        print("Hello, world!")
