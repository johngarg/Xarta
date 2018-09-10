"""The info command."""


from json import dumps

from .base import Base
from ..utils import get_arxiv_data, read_xarta_file
from ..database import PaperDatabase


class Info(Base):
    """Print all of the information about the paper"""

    def run(self):
        options = self.options
        ref = options['<ref>']

        database_path = read_xarta_file()
        paper_database = PaperDatabase(database_path)
        info = paper_database.query_papers_contains(
            paper_id=ref, title=None, author=None, category=None, tags=[], filter=None, silent=True)

        info = info[0]
        print(f'arXiv Ref: {info[0]}')
        print(f'Title: {info[1]}')
        print(f'Authors: {info[2]}')
        print(f'Category: {info[3]}')
        print(f'Tags: {info[4]}')
