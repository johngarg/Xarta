"""The open command."""


from json import dumps
import os

from .base import Base
from ..utils import arxiv_open
from ..database import PaperDatabase

HOME = os.path.expanduser('~')

class Add(Base):
    """ Add an arXiv paper and its metadata to the database. """

    def run(self):
        options = self.options
        ref = options['<ref>']
        tags = options['--tag']

        try:
           with open(HOME+'/.xarta', 'r') as xarta_file:
               database_path = xarta_file.readline()
        except:
            raise Exception('Something went wrong...') # TODO make this error more explicit

        paper_database = PaperDatabase(database_path)
        paper_database.add_paper(paper_id=ref, tags=tags)
