import sqlite3
import os
from .utils import get_arxiv_data

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
        c.execute('''CREATE TABLE papers
                     (id text, title text, abstract text, authors text, category text);''')
        conn.commit()
        conn.close()
        print('Database initialised!')

    def add_paper(self, paper_id, tags):
        """ Add paper to database. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        data = get_arxiv_data(paper_id)
        c.execute(f'''INSERT INTO papers (id, title, abstract, authors, category, tags) VALUES ({data['id']}, {data['title']}, {data['abstract']}, {data['authors']}, {data['category']}, {tags});''')
        conn.close()
