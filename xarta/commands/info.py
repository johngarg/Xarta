"""The info command."""


from .base import Base
from ..database import PaperDatabase


class Info(Base):
    """Print all of the information about the paper"""

    def run(self):
        options = self.options
        ref = options["<ref>"]

        with PaperDatabase() as paper_database:
            info = paper_database.query_papers(
                paper_id=ref,
                title=None,
                author=None,
                category=None,
                tags=[],
                filter_=None,
                silent=True,
            )

            info = info[0]
            print(f"arXiv Ref: {info[0]}")
            print(f"Title: {info[1]}")
            print(f"Authors: {info[2]}")
            print(f"Category: {info[3]}")
            print(f"Tags: {info[4]}")
