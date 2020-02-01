"""The info command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_and_validate_ref


class Info(BaseCommand):
    """Print all of the information about the paper"""

    def run(self):
        options = self.options
        ref = options["<ref>"]

        with PaperDatabase() as paper_database:
            processed_ref = process_and_validate_ref(ref, paper_database)
            paper_database.assert_contains(processed_ref)
            info = paper_database.query_papers(
                paper_id=processed_ref,
                title=None,
                author=None,
                category=None,
                tags=[],
                filter_=None,
                silent=True,
            )

            if len(info) == 0:
                raise XartaError("Paper not found.")
            info = info[0]
            print(f"arXiv Ref: {info[0]}")
            print(f"Title: {info[1]}")
            print(f"Authors: {info[2]}")
            print(f"Category: {info[3]}")
            print(f"Tags: {info[4]}")
            print(f"Alias: {info[5]}")
