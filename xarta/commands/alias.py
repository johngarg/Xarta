"""The paper aliasing command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_ref, is_valid_ref, XartaError


class Alias(BaseCommand):
    """ Edit the alias information in the database for a paper. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        alias = options["<alias>"]
        alias = alias or ""

        with PaperDatabase() as paper_database:
            processed_ref = process_ref(ref)
            if is_valid_ref(processed_ref):
                paper_database.set_paper_alias(paper_id=processed_ref, alias=alias)
            else:
                raise XartaError("Not a valid arXiv reference or alias: " + ref)
