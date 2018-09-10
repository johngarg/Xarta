"""The browse command."""


from json import dumps
import os

from .base import Base
from ..utils import arxiv_open, read_xarta_file
from ..database import PaperDatabase


# xarta lucky [--author=<auth>] [--tag=<tg>] [--title=<ttl>] [--ref=<ref>] [--pdf]

class Lucky(Base):
    """ List papers (by metadata). """

    def run(self):
        options = self.options
        tag = options['--tag']
        filter = options['--filter']
        author = options['--author']
        title = options['--title']
        pdf = options['--pdf']

        database_path = read_xarta_file()
        paper_database = PaperDatabase(database_path)
        ans = paper_database.query_papers_contains(
            paper_id=None, category=None, title=title, author=author, tags=tag, filter=filter
        )
        lucky_paper_ref = ans[0][0]
        arxiv_open(lucky_paper_ref, pdf)
