"""The delete command."""


import os

from .base import Base
from ..database import PaperDatabase

HOME = os.path.expanduser('~')

class Delete(Base):
    """ Remove an arXiv paper and its metadata from the database. """

    def run(self):
        options = self.options
        ref = options['<ref>']

        try:
           with open(HOME+'/.xarta', 'r') as xarta_file:
               database_path = xarta_file.readline()
        except:
            raise Exception('Something went wrong...') # TODO make this error more explicit

        paper_database = PaperDatabase(database_path)
        paper_database.delete_paper(ref)
