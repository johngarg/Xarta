"""The browse command."""


from json import dumps
import os

from .base import Base
from ..utils import arxiv_open
from ..database import PaperDatabase

HOME = os.path.expanduser('~')

# xarta browse [--author=<auth>] [--tag=<tg>] [--title=<ttl>] [--ref=<ref>]

class Browse(Base):
    """ List papers (by metadata). """

    def run(self):
        options = self.options
        ref = options['--ref']
        tag = options['--tag']
        author = options['--author']
        category = options['--category']
        title = options['--title']
        all_flag = options['--all']

        try:
           with open(HOME+'/.xarta', 'r') as xarta_file:
               database_path = xarta_file.readline()
        except:
            raise Exception('Something went wrong...') # TODO make this error more explicit

        paper_database = PaperDatabase(database_path)
        if all_flag:
            paper_database.query_papers()
        else:
            paper_database.query_papers_contains(paper_id=ref, title=title, author=author, category=category, tag=tag)
