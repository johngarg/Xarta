"""The delete command."""


import os

from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_ref, is_valid_ref, XartaError


class Delete(BaseCommand):
    """ Remove an arXiv paper and its metadata from the database. """

    def run(self):
        options = self.options
        ref = options["<ref>"]

        with PaperDatabase() as paper_database:
            ref = process_ref(ref)
            if is_valid_ref(ref):
                paper_database.delete_paper(ref)
            else:
                raise XartaError("Not a valid arXiv reference or alias: " + ref)
