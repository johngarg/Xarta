"""The export command."""

from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import XartaError, process_and_validate_ref


class Export(BaseCommand):
    """
    Export the database.
    Currently only exporting to a bibtex file is supported.
    """

    def run(self):
        options = self.options
        bibtex_file = options["<bibtex-file>"]
        ref = options["--ref"]
        tag = options["<tag>"]
        filter_ = options["--filter"]
        author = options["--author"]
        category = options["--category"]
        title = options["--title"]

        with PaperDatabase(self.database_path) as paper_database:
            if (ref or filter_ or author or category or title) is None and (
                tag is None or tag == []
            ):
                # no search criteria, export all papers
                papers = paper_database.get_all_papers()
            else:

                processed_ref = process_and_validate_ref(ref, paper_database)
                papers = paper_database.query_papers(
                    paper_id=processed_ref,
                    title=title,
                    author=author,
                    category=category,
                    tags=tag,
                    filter_=filter_,
                    silent=True,
                )

            paper_refs = [paper_data[0] for paper_data in papers]

            with open(bibtex_file, "w+") as f:

                for ref in paper_refs:

                    bibtex_arxiv, bibtex_inspire = paper_database.get_bibtex_data(
                        ref, insert_alias=options["--export-alias"]
                    )

                    if options["arxiv"] or bibtex_inspire == "":
                        f.write(bibtex_arxiv + "\n\n")
                    elif options["inspire"] or bibtex_arxiv == "":
                        f.write(bibtex_inspire + "\n\n")

                print(bibtex_file + " successfully written!")
