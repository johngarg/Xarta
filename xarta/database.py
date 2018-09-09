import sqlite3
import os
from .utils import get_arxiv_data, list_to_string, expand_tag
import pdb

HOME = os.path.expanduser('~')

class PaperDatabase():
    def __init__(self, path):
        self.path = path

    def create_connection(self):
        """ Create a database connection to a SQLite database. """
        print('Creating new database at ' + self.path + '...')
        conn = sqlite3.connect(self.path)
        conn.close()
        with open(HOME+'/.xarta', 'w') as xarta_file:
            xarta_file.write(self.path)

    def initialise_database(self):
        """ Initialise database with empty table. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        print('Initialising database...')
        c.execute('''CREATE TABLE papers (id text, title text, authors text, category text, tags text);''')
        # c.execute('''CREATE TABLE tags (abbrev text, full text);''') # TODO fix this up...
        conn.commit()
        conn.close()
        print('Database initialised!')

    # TODO add check to see if paper already in database
    def add_paper(self, paper_id, tags):
        """ Add paper to database. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        data = get_arxiv_data(paper_id)
        author_string = list_to_string(data['authors'])
        tags = [expand_tag(tag, data) for tag in tags]
        tags = list_to_string(tags)

        insert_command = f'''INSERT INTO papers (id, title, authors, category, tags) VALUES ("{paper_id}", "{data['title']}", "{author_string}", "{data['category']}", "{tags}");'''
        c.execute(insert_command)
        print(f"{paper_id} added to database!")
        conn.commit()
        conn.close()


    def add_local_paper(self, paper_id, tags, path, title='', authors=[]):
        """ Add paper to database. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        data = {'title': title, 'authors': authors, 'category': 'local'}
        author_string = list_to_string(data['authors'])
        tags = [expand_tag(tag, data) for tag in tags]
        tags = list_to_string(tags)

        insert_command = f'''INSERT INTO papers (id, title, authors, category, tags) VALUES ("{paper_id}", "{data['title']}", "{author_string}", "{data['category']}", "{tags}");'''
        c.execute(insert_command)
        print(f"{paper_id} added to database from {path}!")
        conn.commit()
        conn.close()


    def delete_paper(self, paper_id):
        """ Remove paper from database. """

        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        data = get_arxiv_data(paper_id)
        delete_command = f'''DELETE FROM papers WHERE id = "{paper_id}";'''
        c.execute(delete_command)
        print(f"{paper_id} deleted from database!")
        conn.commit()
        conn.close()

    def query_papers(self, silent=False):
        """ Query information about a paper in the databse. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        query_command = f'''SELECT * FROM papers;'''
        query_results = c.execute(query_command)
        all_rows = c.fetchall()
        
        # get current console window dimensions
        term_rows, term_columns = os.popen('stty size', 'r').read().split()
        l = (int(term_columns) // 5) - 1 # max chars in col
        data = [[(c if len(c) < l else c[:(l-3)] + "...") 
                 for c in row] 
                for row in all_rows]

        if not silent:
            from tabulate import tabulate
            to_be_printed = [['arXiv:'+row[0], *row[1:]] for row in data]
            print(
                tabulate(to_be_printed,
                         headers=['Ref', 'Title', 'Authors', 'Category', 'Tags'],
                         tablefmt="simple"))
        conn.close()
        return all_rows

    def query_papers_contains(self, paper_id, title, author, category, tags,
                              silent=False, select=False):
        """
        Function to search and filter paper database. Returns a list of
        tuples and (if `silent` is False) prints a table to the screen. Search
        parameters connected by a logical OR, thus:
           db.query_papers_contains(paper_id=None,
                                    title=None,
                                    author='Weinberg',
                                    category='hep-th',
                                    tags=[])
        will return every paper in the database from 'hep-th' as well as those
        by 'Weinberg'.
        """
        library_data = self.query_papers(silent=True)
        data = []
        for row in library_data:
            if paper_id is not None and paper_id in row[0]:
                data.append(row)
                continue
            elif title is not None and title in row[1]:
                data.append(row)
                continue
            elif author is not None and author in row[2]:
                data.append(row)
                continue
            elif category is not None and category in row[3]:
                data.append(row)
                continue
            elif tags is not None and tags != []:
                added = False  # don't include the same paper twice
                for tag in tags:
                    if tag in row[4] and not added:
                        data.append(row)
                        added = True

        if not silent:
            from tabulate import tabulate
            short_data = [[(c if len(c) < 40 else c[:37] + "...")
                           for c in row]
                          for row in data]
            to_be_printed = [['arXiv:'+row[0], *row[1:]] for row in short_data]
            print(
                tabulate(to_be_printed,
                         headers=['Ref', 'Title', 'Authors', 'Category', 'Tags'],
                         tablefmt="simple",
                         showindex=(True if select else False)))

        return to_be_printed

    def contains(self, ref):
        """
        Returns a boolean identifying if an entry with reference `ref` exists
        within the database.
        """
        search_results = self.query_papers_contains(
            paper_id=ref,
            title=None,
            author=None,
            category=None,
            tags=[],
            silent=True)
        return bool(search_results)
