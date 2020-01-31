"""PaperDatabase class."""

import sqlite3
import os
from . import utils
from .utils import XartaError


HOME = os.path.expanduser("~")

DATA_HEADERS = ("Ref", "Title", "Authors", "Category", "Tags", "Alias")


def initialise_database(database_location, config_file=HOME + "/.xarta"):
    """Initialise database with empty table and update file that points to database.
    If database already exists, just update the file"""

    # resolve relative paths, e.g., 'xarta init ./'
    database_location = os.path.abspath(database_location)

    # verify folder exists
    if not os.path.isdir(database_location):
        raise XartaError("Directory does not exist.")

    # create xarta directory
    database_location += "/.xarta.d"
    os.makedirs(database_location, exist_ok=True)
    database_path = database_location + "/db.sqlite3"

    # check if file already exists
    if "db.sqlite3" not in os.listdir(database_location):

        print("Creating new database at " + database_path + "...")

        init_command = 'CREATE TABLE papers (id text UNIQUE, title text, authors text, category text, tags text, alias text DEFAULT "" );'

        with sqlite3.connect(database_path) as connection:
            print("Initialising database...")
            connection.execute(init_command)
        connection.close()

        print("Database initialised!")
    else:

        print(database_path + " already exists.")

    write_database_path(database_path, config_file=config_file)


def write_database_path(database_path, config_file):
    """Write database location to a file, usually  ~/.xarta """
    with open(config_file, "w") as xarta_file:
        xarta_file.write(database_path)
    print(f"Database location saved to {config_file}")


def read_database_path(config_file):
    """Read database location from a file, usually ~/.xarta, and return path as a string."""
    try:
        with open(config_file, "r") as xarta_file:
            return xarta_file.readline()
    except:
        raise XartaError(
            f"Could not read database directory from '{config_file}'. Have you initialised a database?"
        )


class PaperDatabase:
    """The paper database interface."""

    def __init__(self, path=None, config_file=HOME + "/.xarta"):
        self.config_file = config_file
        self.path = path
        self.connection = None
        self.cursor = None

    def __enter__(self):
        if self.path is None:
            self.path = read_database_path(self.config_file)
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
        xarta, insert new rows"""
        self.cursor.execute("PRAGMA table_info(papers)")
        columns = self.cursor.fetchall()
        if len(columns) == 5:
            # v1 database. Is missing the alias column!
            print("Updating database file.")
            self.cursor.execute('ALTER TABLE papers ADD alias text DEFAULT "" ')

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
        tags = utils.list_to_string(tags)
        title, category = data["title"], data["category"]
        insert_command = "INSERT INTO papers (id, title, authors, category, tags, alias) VALUES (?, ?, ?, ?, ?, ?);"

        self.cursor.execute(
            insert_command, (paper_id, title, authors, category, tags, alias)
        )

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
            "UPDATE papers SET alias = ? WHERE id = ?;", (alias, paper_id),
        )
        if alias:
            print(f"{paper_id} is now aliased to: {alias}")
        else:
            print(f"Removed alias from {paper_id}")

    def edit_paper_tags(self, paper_id, tags, action):
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
        elif action == "delete":
            # remove tags from old_tags
            old_tags = self.get_tags(paper_id)
            new_tags = [tag for tag in old_tags if tag not in tags]
        else:
            raise XartaError("Unkown edit action: " + action)

        new_tags = utils.list_to_string(new_tags)
        self.cursor.execute(
            f"""UPDATE papers SET tags = ?
                                WHERE id = ?;""",
            (new_tags, paper_id),
        )

        print(f"{paper_id} now has the following tags in the database: {new_tags}")

    def get_all_papers(self):
        """Get all papers"""
        query_command = f"""SELECT * FROM papers;"""
        self.cursor.execute(query_command)
        return self.cursor.fetchall()

    def print_all_papers(self):
        """Print a table of all the papers"""
        library_data = self.get_all_papers()

        from tabulate import tabulate

        # get current console window dimensions
        data = utils.format_data_term(library_data)

        # prepend arXiv to ref to distinguish from cern doc server papers
        to_be_printed = []
        for row in data:
            new_row = row
            new_row[0] = "arXiv:" + row[0]
            to_be_printed.append(new_row)

        print(tabulate(to_be_printed, headers=list(DATA_HEADERS), tablefmt="simple"))

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
    ):
        """Function to search and filter paper database. Returns a list of
        tuples and (if `silent` is False) prints a table to the screen. Search
        parameters connected by a logical OR, thus:

            db.query_papers_contains(paper_id=None, title=None,
                                     author='Weinberg', category='hep-th',
                                     tags=[])

        will return every paper in the database from 'hep-th' as well as those
        by 'Weinberg'.
        """
        library_data = self.get_all_papers()
        data = []
        col_names = ["ref", "title", "authors", "category", "tags"]
        for row in library_data:
            row_dict = dict(zip(col_names, row))
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
                lambda_prestring = "lambda " + ", ".join(col_names) + ": "
                if eval(lambda_prestring + filter_)(*row_dict.values()):
                    data.append(row)
                    continue

        if len(data) > 0 and not silent:
            from tabulate import tabulate

            short_data = utils.format_data_term(data, select)
            to_be_printed = [["arXiv:" + row[0], *row[1:]] for row in short_data]
            print(
                tabulate(
                    to_be_printed,
                    headers=list(DATA_HEADERS),
                    tablefmt="simple",
                    showindex=(True if select else False),
                )
            )

        return data

    def contains(self, ref):
        """Returns a boolean identifying if an entry with reference `ref`
        exists within the database.
        """
        search_results = self.query_papers(
            paper_id=ref,
            title=None,
            author=None,
            category=None,
            tags=[],
            filter_=None,
            silent=True,
        )
        return bool(search_results)
