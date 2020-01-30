"""The choose command."""


from .base import Base
from ..utils import arxiv_open
from ..database import PaperDatabase


class Choose(Base):
    """ List papers (by metadata) with an option to open. """

    def run(self):
        options = self.options
        pdf = options["--pdf"]
        ref = options["--ref"]
        filter_ = options["--filter"]
        tag = options["<tags>"]
        author = options["--author"]
        category = options["--category"]
        title = options["--title"]

        paper_database = PaperDatabase()
        paper_data = paper_database.query_papers_contains(
            paper_id=ref,
            title=title,
            author=author,
            category=category,
            tags=tag,
            filter_=filter_,
            select=True,
        )

        choice = int(input("Paper to open: "))
        ref_to_open = paper_data[choice][0]
        arxiv_open(ref_to_open, pdf=pdf)
