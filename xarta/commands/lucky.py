"""The browse command."""


from .base import Base
from ..utils import arxiv_open
from ..database import PaperDatabase


class Lucky(Base):
    """ List papers (by metadata). """

    def run(self):
        options = self.options
        tag = options["<tags>"]
        filter_ = options["--filter"]
        author = options["--author"]
        title = options["--title"]
        pdf = options["--pdf"]

        paper_database = PaperDatabase()
        ans = paper_database.query_papers_contains(
            paper_id=None,
            category=None,
            title=title,
            author=author,
            tags=tag,
            filter_=filter_,
        )
        lucky_paper_ref = ans[0][0]
        arxiv_open(lucky_paper_ref, pdf)
