"""The delete command."""


import os

from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_and_validate_ref


class Delete(BaseCommand):
    """ Remove an arXiv paper and its metadata from the database. """

    def run(self):
        options = self.options
        ref = options["<ref>"]

        with PaperDatabase() as paper_database:
            processed_ref = process_and_validate_ref(ref, paper_database)
            paper_database.check_ref_exists(processed_ref)
            paper_database.delete_paper(processed_ref)
