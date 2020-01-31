"""The paper aliasing command."""


from .base import Base
from ..database import PaperDatabase


class Alias(Base):
    """ Edit the alias information in the database for a paper. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        alias = options["<alias>"]
        alias = alias or ""

        with PaperDatabase() as paper_database:
            paper_database.set_paper_alias(paper_id=ref, alias=alias)
