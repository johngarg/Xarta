"""The delete command."""


import os

from .base import Base
from ..database import PaperDatabase


class Delete(Base):
    """ Remove an arXiv paper and its metadata from the database. """

    def run(self):
        options = self.options
        ref = options["<ref>"]

        with PaperDatabase() as paper_database:
            paper_database.delete_paper(ref)
