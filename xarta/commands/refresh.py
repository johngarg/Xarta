"""The refresh command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import XartaError, process_and_validate_ref


class Refresh(BaseCommand):
    """Refreshes information about a paper from the arxiv. Usefull if new versions
    were released with updated information."""

    def run(self):
        options = self.options
        ref = options["<ref>"]

        with PaperDatabase(self.database_path) as paper_database:
            processed_ref = process_and_validate_ref(ref, paper_database)
            paper_database.refresh_paper(processed_ref)
