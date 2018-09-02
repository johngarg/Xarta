"""The choose command."""


from json import dumps
import os

from .base import Base
from ..utils import arxiv_open, read_xarta_file
from ..database import PaperDatabase


class Choose(Base):
    """ List papers (by metadata) with an option to open. """

    def run(self):
        options = self.options
        pdf = options['--pdf']
        ref = options['--ref']
        tag = options['--tag']
        author = options['--author']
        category = options['--category']
        title = options['--title']

        database_path = read_xarta_file()
        paper_database = PaperDatabase(database_path)
        paper_data = paper_database.query_papers_contains(paper_id=ref, title=title, author=author, category=category, tags=tag, select=True)

        choice = int(input('Paper to open: '))
        ref_to_open = paper_data[choice][0]
        arxiv_open(ref_to_open, pdf=pdf)