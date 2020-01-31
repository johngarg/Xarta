"""The init command."""


from .base import Base
from ..database import PaperDatabase


class Hello(Base):
    """ Initialise database """

    def run(self):
        print("Hello, world!")
