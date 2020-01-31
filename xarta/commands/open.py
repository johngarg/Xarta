"""The open command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import arxiv_open, process_and_validate_ref


class Open(BaseCommand):
    """Open an arXiv paper with reference"""

    def run(self):
        options = self.options
        ref = options["<ref>"]
        pdf = options["--pdf"]

        with PaperDatabase() as paper_database:
            processed_ref = process_and_validate_ref(ref, paper_database)
            arxiv_open(processed_ref, pdf=pdf)
