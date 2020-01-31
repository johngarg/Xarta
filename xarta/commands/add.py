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

        for tag in tags:
            if ";" in tag:
                raise XartaError("Invalid tag, tags cannot contain semicolons.")

        with PaperDatabase() as paper_database:
            processed_ref = process_ref(ref)
            if is_valid_ref(processed_ref):
                paper_database.add_paper(paper_id=processed_ref, tags=tags, alias=alias)
            else:
                raise XartaError("Not a valid arXiv reference or alias: " + ref)
