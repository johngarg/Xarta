"""The open command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_ref, is_valid_ref, XartaError


class Add(BaseCommand):
    """ Add an arXiv paper and its metadata to the database. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        tags = options["<tag>"]
        alias = options["--alias"] or ""

        with PaperDatabase() as paper_database:
            ref = process_ref(ref)
            if is_valid_ref(ref):
                paper_database.add_paper(paper_id=ref, tags=tags, alias=alias)
            else:
                raise XartaError("Not a valid arXiv reference or alias: " + ref)
