"""The browse command."""


from .base import Base
from ..utils import read_xarta_file
from ..database import PaperDatabase


# xarta browse [--author=<auth>] [--tag=<tg>] [--title=<ttl>] [--ref=<ref>]

class Browse(Base):
    """ List papers (by metadata). """

    def run(self):
        options = self.options
        ref = options['--ref']
        tag = options['--tag']
        filter = options['--filter']
        author = options['--author']
        category = options['--category']
        title = options['--title']
        all_flag = options['--all']

        database_path = read_xarta_file()
        paper_database = PaperDatabase(database_path)
        if all_flag:
            paper_database.query_papers()
        else:
            paper_database.query_papers_contains(
                paper_id=ref, title=title, author=author, category=category, tags=tag, filter=filter
            )
