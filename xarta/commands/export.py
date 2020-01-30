"""The export command."""


from arxivcheck.arxiv import check_arxiv_published

from .base import Base
from ..database import PaperDatabase
from ..utils import XartaError


class Export(Base):
    """
    Export the database.
    Currently only exporting to a bibtex file is supported.
    <export-path> should be a path to a directory.
    """

    def run(self):
        options = self.options
        export_path = options["<export-path>"]
        tags = options["<tag>"]

        if export_path is None:
            raise XartaError("<export-path> unspecified.")

        with PaperDatabase() as paper_database:

            if tags != []:
                good_papers = paper_database.query_papers(
                    paper_id=None,
                    title=None,
                    author=None,
                    category=None,
                    tags=tags,
                    filter_=None,
                    silent=True,
                )
            else:
                good_papers = paper_database.get_all_papers()

            good_paper_refs = [paper_data[0] for paper_data in good_papers]

            with open(export_path + "/xarta.bib", "w+") as f:
                for ref in good_paper_refs:
                    bib_info = check_arxiv_published(ref)
                    if bib_info[0]:
                        print("Writing bibtex entry for " + ref)
                        f.write(bib_info[2] + "\n\n")

                print(export_path + "/xarta.bib" + " successfully written!")
