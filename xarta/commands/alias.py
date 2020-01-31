"""The paper aliasing command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_and_validate_ref


class Alias(BaseCommand):
    """ Edit the alias information in the database for a paper. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        alias = options["<alias>"]
        alias = alias or ""

        with PaperDatabase() as paper_database:
            processed_ref = process_and_validate_ref(ref, paper_database)
            paper_database.set_paper_alias(paper_id=processed_ref, alias=alias)
