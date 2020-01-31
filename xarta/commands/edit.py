"""The tag editing command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_ref, is_valid_ref, XartaError


class Edit(BaseCommand):
    """ Edit the tag information in the database for a paper. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        tags = options["<tag>"]
        action = options["--action"]

        with PaperDatabase() as paper_database:
            ref = process_ref(ref)
            if is_valid_ref(ref):
                paper_database.edit_paper_tags(paper_id=ref, tags=tags, action=action)
            else:
                raise XartaError("Not a valid arXiv reference or alias: " + ref)
