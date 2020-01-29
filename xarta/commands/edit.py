"""The edit command."""


from .base import Base
from ..utils import read_xarta_file
from ..database import PaperDatabase


class Edit(Base):
    """ Edit the information in the database for a paper. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        tags = options["--tag"]

        database_path = read_xarta_file()
        paper_database = PaperDatabase(database_path)

        paper_database.edit_paper_tags(paper_id=ref, new_tags=tags)
