"""The open command."""


from .base import Base
from ..database import PaperDatabase


class Add(Base):
    """ Add an arXiv paper and its metadata to the database. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        tags = options["<tag>"]

        with PaperDatabase() as paper_database:
            paper_database.add_paper(paper_id=ref, tags=tags)
