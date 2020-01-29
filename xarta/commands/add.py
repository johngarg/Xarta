"""The open command."""


from .base import Base
from ..utils import read_xarta_file
from ..database import PaperDatabase


class Add(Base):
    """ Add an arXiv paper and its metadata to the database. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        tags = options["<tags>"]

        database_path = read_xarta_file()
        paper_database = PaperDatabase(database_path)

        paper_database.add_paper(paper_id=ref, tags=tags)
