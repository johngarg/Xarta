"""The browse command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_and_validate_ref


class Browse(BaseCommand):
    """ List papers (by metadata). """

    def run(self):
        options = self.options
        ref = options["--ref"]
        tag = options["<tag>"]
        filter_ = options["--filter"]
        author = options["--author"]
        category = options["--category"]
        title = options["--title"]

        with PaperDatabase() as paper_database:
            if (ref or filter_ or author or category or title) is None and (
                tag is None or tag == []
            ):
                # no search criteria, show all papers
                paper_database.print_all_papers()
            else:

                processed_ref = process_and_validate_ref(ref, paper_database)
                paper_database.query_papers(
                    paper_id=processed_ref,
                    title=title,
                    author=author,
                    category=category,
                    tags=tag,
                    filter_=filter_,
                )
