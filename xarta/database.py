"""PaperDatabase class."""

import sqlite3
import os
from . import utils
from .utils import XartaError, string_to_list, check_filter_is_sanitary, print_table
import requests
from arxivcheck.arxiv import check_arxiv_published

DATA_HEADERS = ["ref", "title", "authors", "category", "tags", "alias"]


def initialise_database(database_path):
    """Initialise database with empty table. If file already exists, do nothing"""

    if os.path.isfile(database_path):
        print(database_path + " already exists.")
        return

    print("Creating new database at " + database_path + "...")

    init_command = 'CREATE TABLE papers (id text UNIQUE, title text, authors text, category text, tags text, alias text DEFAULT "", bibtex_arxiv text DEFAULT "" , bibtex_inspire text DEFAULT ""  );'

    with sqlite3.connect(database_path) as connection:
        print("Initialising database...")
        connection.execute(init_command)
        connection.commit()
    connection.close()

    print("Database initialised!")


class PaperDatabase:
    """The paper database interface."""

    def __init__(self, path):
        self.path = path
        self.connection = None
        self.cursor = None

        if self.path is None:
            raise XartaError("Database path not found! Have you initialised it?")

        if not os.path.isfile(self.path):
            raise XartaError("Database does not exist in " + path)

    def __enter__(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        self.check_database_version()
        return self

    def __exit__(self, error_type, value, traceback):
        if traceback is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.cursor.close()
        self.connection.close()

    def check_database_version(self):
        """Check version of database. If database was created using an older version of
        xarta, insert new rows. Using total number of rows as a placeholder
        'version' idetntifier

        """
        self.cursor.execute("PRAGMA table_info(papers)")
        columns = self.cursor.fetchall()
        if len(columns) == 5:
            # v1 database. Is missing the alias and the two bibtex columns!
            print("Updating database file to v3.")
            self.cursor.execute('ALTER TABLE papers ADD COLUMN alias text DEFAULT "";')
            self.cursor.execute(
                'ALTER TABLE papers ADD COLUMN bibtex_arxiv text DEFAULT "";'
            )
            self.cursor.execute(
                'ALTER TABLE papers ADD COLUMN bibtex_inspire text DEFAULT "";'
            )

        elif len(columns) == 6:
            # v2 database. Is missing the the two bibtex columns!
            print("Updating database file to v3.")
            self.cursor.execute(
                'ALTER TABLE papers ADD COLUMN bibtex_arxiv text DEFAULT "";'
            )
            self.cursor.execute(
                'ALTER TABLE papers ADD COLUMN bibtex_inspire text DEFAULT "";'
            )

    def get_all_aliases(self):
        """get a list of all aliases."""
        self.cursor.execute("SELECT alias FROM papers")
        results = self.cursor.fetchall()
        aliases = [row[0] for row in results]
        return aliases

    def resolve_alias(self, alias):
        """Find the paper_id associated with an alias. Return False if the alias does
        not exist"""
        self.cursor.execute("SELECT id FROM papers WHERE alias=?", (alias,))
        results = self.cursor.fetchall()
        if not results:
            return ""
        return results[0][0]

    def refresh_paper(self, paper_id):
        """Referesh arxiv info on paper (e.g., get newest version.)"""

        if not self.contains(paper_id):
            raise XartaError("This paper is not in the database.")

        data = utils.get_arxiv_data(paper_id)
        authors = utils.list_to_string(data["authors"])
        title, category = data["title"], data["category"]
        # tags = [utils.expand_tag(tag, data) for tag in tags]
        insert_command = (
            "UPDATE papers SET title = ?, authors = ?, category = ? WHERE id = ? ;"
        )

        self.cursor.execute(insert_command, (title, authors, category, paper_id))

        # update bibtex
        self.get_bibtex_data(paper_id, force_refresh=True)

        print(f"{paper_id} information has been updated!")

    def add_paper(self, paper_id, tags, alias):
        """Add paper to database. paper_id is the arxiv number as a string. The
        tags are a list of strings.
        """
        if alias and alias in self.get_all_aliases():
            raise XartaError("Alias is not unique!")

        if self.contains(paper_id):
            raise XartaError("This paper is already in the database.")

        data = utils.get_arxiv_data(paper_id)
        authors = utils.list_to_string(data["authors"])
        # tags = [utils.expand_tag(tag, data) for tag in tags]
        tags.sort(key=str.lower)
        tags = utils.list_to_string(tags)
        title, category = data["title"], data["category"]
        insert_command = "INSERT INTO papers (id, title, authors, category, tags, alias) VALUES (?, ?, ?, ?, ?, ?);"

        self.cursor.execute(
            insert_command, (paper_id, title, authors, category, tags, alias)
        )

        # get bibtex data
        self.get_bibtex_data(paper_id)

        print(f"{paper_id} added to database!")

    def delete_paper(self, paper_id):
        """Remove paper from database."""
        self.cursor.execute("DELETE FROM papers WHERE id = ?;", (paper_id,))

        print(f"{paper_id} deleted from database!")

    def get_tags(self, paper_id):
        """Get list of tags for some paper"""
        self.cursor.execute("SELECT tags FROM papers WHERE id=?;", (paper_id,))
        tags_string = self.cursor.fetchall()[0][0]
        return utils.string_to_list(tags_string)

    def set_paper_alias(self, paper_id, alias):
        """Edit the alias of a paper in the database."""

        self.cursor.execute(
            "UPDATE papers SET alias = ? WHERE id = ?;",
            (alias, paper_id),
        )
        if alias:
            print(f"{paper_id} is now aliased to: {alias}")
        else:
            print(f"Removed alias from {paper_id}")

    def rename_tag(self, old_tag, new_tag=None):
        """Rename or remove a tag from every paper"""

        matching_papers = self.query_papers(
            None, None, None, None, [old_tag], None, silent=True, exact_tags=True
        )
        for paper in matching_papers:
            self.edit_paper_tags(
                paper_id=paper[0],
                tags=[old_tag],
                action="remove",
                silent=True,
            )
            if new_tag is not None:
                self.edit_paper_tags(
                    paper_id=paper[0],
                    tags=[new_tag],
                    action="add",
                    silent=True,
                )

        if new_tag is None:
            print(f"All instances of the tag '{old_tag}' were removed")
        else:
            print(
                f"All instances of the tag '{old_tag}' were replaced with '{new_tag}'"
            )

    def edit_paper_tags(self, paper_id, tags, action, silent=False):
        """Edit paper tags in database."""
        # first: remove duplicates in tags
        tags = list(set(tags))

        if action == "set":
            new_tags = tags
        elif action == "add":
            # add tags to old_tags, but dont add duplicates
            old_tags = self.get_tags(paper_id)
            tags = [tag for tag in tags if tag not in old_tags]
            new_tags = old_tags + tags
        elif action == "remove":
            # remove tags from old_tags
            old_tags = self.get_tags(paper_id)
            new_tags = [tag for tag in old_tags if tag not in tags]
        else:
            raise XartaError("Unkown tag editing action: " + action)

        new_tags.sort(key=str.lower)
        new_tags = utils.list_to_string(new_tags)
        self.cursor.execute(
            f"""UPDATE papers SET tags = ?
                                WHERE id = ?;""",
            (new_tags, paper_id),
        )

        if not silent:
            print(f"{paper_id} now has the following tags in the database: {new_tags}")

    def get_bibtex_data(self, paper_id, force_refresh=False):
        """Get bibtex data for a paper. If it is not in the database, try and download it."""

        self.cursor.execute("SELECT bibtex_arxiv FROM papers WHERE id=?", (paper_id,))
        bibtex_arxiv = self.cursor.fetchall()[0][0]

        if bibtex_arxiv == "" or force_refresh:
            # get data from arxiv using the arxivcheck package
            print("Updating arxiv bibtex for", paper_id)
            bib_info = check_arxiv_published(paper_id)
            if bib_info[0]:
                bibtex_arxiv = bib_info[2] + "\n"
                self.cursor.execute(
                    f"""UPDATE papers SET bibtex_arxiv = ?
                                        WHERE id = ?;""",
                    (bibtex_arxiv, paper_id),
                )

        self.cursor.execute("SELECT bibtex_inspire FROM papers WHERE id=?", (paper_id,))
        bibtex_inspire = self.cursor.fetchall()[0][0]
        if bibtex_inspire == "" or force_refresh:
            print("Updating inspire bibtex for", paper_id)
            # request data from inspire
            # format should work for both old and new arxiv ids
            url = "https://inspirehep.net/api/arxiv/" + paper_id + "?format=bibtex"
            response = requests.get(url)

            # raise error if HTTPS error was returned
            response.raise_for_status()

            bibtex_inspire = response.text

            self.cursor.execute(
                f"""UPDATE papers SET bibtex_inspire = ?
                                    WHERE id = ?;""",
                (bibtex_inspire, paper_id),
            )

        return (bibtex_arxiv, bibtex_inspire)

    def get_all_papers(self):
        """Get all papers"""
        query_command = f"""SELECT * FROM papers;"""
        self.cursor.execute(query_command)
        return self.cursor.fetchall()

    def print_all_papers(self, select=False):
        """Print a table of all the papers"""
        data = self.get_all_papers()
        print_table(data, DATA_HEADERS, select)
        if select:
            return data

    def query_papers(
        self,
        paper_id,
        title,
        author,
        category,
        tags,
        filter_,
        silent=False,
        select=False,
        exact_tags=False,
    ):
        """Function to search and filter paper database. Returns a list of
        tuples and (if `silent` is False) prints a table to the screen. Search
        parameters connected by a logical OR, thus:

            db.query_papers_contains(paper_id=None, title=None,
                                     author='Weinberg', category='hep-th',
                                     tags=[])

        will return every paper in the database from 'hep-th' as well as those
        by 'Weinberg'. The exact_tags option determines how tag-matching is
        done. If exact_tags=False, then a search for quarks will return both
        papers tagged as quarks and leptoquarks.
        """

        if filter_ is not None:
            # check if the provided filter is sanitary/safe.
            # throws errors with helpfull messages if not sanitary
            check_filter_is_sanitary(filter_, DATA_HEADERS)

        library_data = self.get_all_papers()
        data = []
        for row in library_data:
            row_dict = dict(zip(DATA_HEADERS, row))
            if exact_tags:
                # tags are currently a long, comma separated, string. using the
                # "in" keyword searches the string. By converting it to a list of
                # tags, the 'in' keyword will match only complete tags in the
                # list.
                row_dict["tags"] = string_to_list(row_dict["tags"])

            if paper_id is not None and paper_id in row_dict["ref"]:
                data.append(row)
                continue
            elif title is not None and title in row_dict["title"]:
                data.append(row)
                continue
            elif author is not None and author in row_dict["authors"]:
                data.append(row)
                continue
            elif category is not None and category in row_dict["category"]:
                data.append(row)
                continue
            elif tags is not None and tags != []:
                for tag in tags:
                    if tag in row_dict["tags"]:
                        data.append(row)
                        break  # Don't include same paper twice
                continue
            elif filter_ is not None:
                try:
                    # use a dict to define accesibe variables in the eval: even though
                    # variable names should not be capitalised, users may try and write
                    # the variables as they appear in the table header (capitalised). so
                    # I am including capitalised variables
                    eval_vars = {"__builtins__": {}}
                    eval_vars.update(row_dict)
                    for k in DATA_HEADERS:
                        eval_vars[k.capitalize()] = eval_vars[k]
                    # evaliate filter!
                    if eval(filter_, eval_vars):
                        data.append(row)
                        continue
                except Exception:
                    raise XartaError("Error when evaluating filter.")

        if not data:
            raise XartaError("No matching papers found!")

        if not silent:
            print_table(data, DATA_HEADERS, select)

        return data

    def contains(self, ref):
        """Returns a boolean identifying if an entry with reference `ref`
        exists within the database.
        """
        self.cursor.execute("SELECT 1 FROM papers WHERE id = ?;", (ref,))
        return bool(self.cursor.fetchall())

    def assert_contains(self, ref):
        """Returns a boolean identifying if an entry with reference `ref`
        exists within the database. If not, raise an error."""
        if not self.contains(ref):
            raise XartaError(f"Reference does not exist in database: {ref}")
