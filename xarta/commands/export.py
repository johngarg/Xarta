"""The export command."""


from arxivcheck.arxiv import check_arxiv_published

from .base import Base
from ..utils import read_xarta_file
from ..database import PaperDatabase


class Export(Base):
    """
    Export the database.
    Currently only exporting to a bibtex file is supported.
    <export-path> should be a path to a directory.
    """

    def run(self):
        options = self.options
        export_path = options["<export-path>"]
        bibtex = options["--bibtex"]
        tags = options["<tags>"]

        database_path = read_xarta_file()
        paper_database = PaperDatabase(database_path)

        if not bibtex:
            raise Exception("Currently bibtex is the only supported export format.")

        if export_path is None:
            raise Exception("<export-path> unspecified.")

        if tags != []:
            good_papers = paper_database.query_papers_contains(
                paper_id=None,
                title=None,
                author=None,
                category=None,
                tags=tags,
                filter_=None,
                silent=True,
            )
        else:
            good_papers = paper_database.query_papers(silent=True)

        good_paper_refs = [paper_data[0] for paper_data in good_papers]

        if bibtex:
            with open(export_path + "xarta.bib", "w+") as f:
                for ref in good_paper_refs:
                    bib_info = check_arxiv_published(ref)
                    if bib_info[0]:
                        print("Writing bibtex entry for " + ref)
                        f.write(bib_info[2] + "\n\n")

            print(export_path + "xarta.bib" + " successfully written!")
