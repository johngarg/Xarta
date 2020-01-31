"""The init command."""


from .base import BaseCommand


class Hello(BaseCommand):
    """ Initialise database """

    def run(self):
        print("Hello, world!")
