"""The tag renaming command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_and_validate_ref, XartaError


class Rename(BaseCommand):
    """ Rename or delete a tag from every paper."""

    def run(self):
        options = self.options
        tags = options["<tag>"]

        for tag in tags:
            if ";" in tag:
                raise XartaError("Invalid tag, tags cannot contain semicolons.")
        if len(tags) > 2:
            raise XartaError("Too many arguments.")

        with PaperDatabase(self.database_path) as paper_database:
            paper_database.rename_tag(*tags)
