"""The browse command."""


from .base import Base
from ..database import PaperDatabase


class Browse(Base):
    """ List papers (by metadata). """

    def run(self):
        options = self.options
        ref = options["--ref"]
        tag = options["<tags>"]
        filter_ = options["--filter"]
        author = options["--author"]
        category = options["--category"]
        title = options["--title"]

        paper_database = PaperDatabase()
        if (ref or filter_ or author or category or title) is None and (
            tag is None or tag == []
        ):
            # no search criteria, show all papers
            paper_database.query_papers()
        else:
            paper_database.query_papers_contains(
                paper_id=ref,
                title=title,
                author=author,
                category=category,
                tags=tag,
                filter_=filter_,
            )
