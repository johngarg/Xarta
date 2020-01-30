"""Some useful functions."""

from sys import platform
from urllib.request import urlopen
import os
import re
import sqlite3
import xmltodict

if platform.startswith("linux"):
    OPEN_COMMAND = "xdg-open "
elif platform.startswith("darwin"):
    OPEN_COMMAND = "open "
else:
    raise ValueError("Xarta is currently not supported on Windows.")

# set of arxiv categories only used for opening the "new" page of results from
# the command line
ARXIV_CATEGORIES = {
    "astro-ph",
    "cond-mat",
    "gr-qc",
    "hep-ex",
    "hep-lat",
    "hep-ph",
    "hep-th",
    "math-ph",
    "nlin",
    "nucl-ex",
    "nucl-th",
    "physics",
    "quant-ph",
    "math",
    "CoRR",
    "q-bio",
    "stat",
    "eess",
    "econ",
}


def is_arxiv_category(s):
    """Returns true if the string s is an arxiv category."""
    return s in ARXIV_CATEGORIES


def is_valid_ref(paper_id):
    """Returns True if s is a valid arXiv reference."""
    is_new_arxiv_ref = bool(re.match("\d{4}\.\d+", paper_id))
    is_old_arxiv_ref = bool(re.match("[\w\-\.]+\/\d+", paper_id))
    return is_new_arxiv_ref or is_old_arxiv_ref


def processed_ref(paper_id, verbose=True):
    # strip version
    proc_paper_id = re.sub("v[0-9]+$", "", paper_id)
    if proc_paper_id != paper_id and verbose:
        print("Stripping version from paper ID.")

    return proc_paper_id


def arxiv_open(ref, pdf=False):
    """Opens arxiv ref in browser."""
    if is_arxiv_category(ref):
        os.system(OPEN_COMMAND + " https://arxiv.org/list/" + ref + "/new")
    elif is_valid_ref(ref):
        if pdf:
            os.system(OPEN_COMMAND + " https://arxiv.org/pdf/" + ref + ".pdf")
        else:
            os.system(OPEN_COMMAND + " https://arxiv.org/abs/" + ref)
    else:
        raise ValueError("`xarta open` received an invalid <ref>.")


def get_arxiv_data(ref):
    """Returns a dictionary of data about the reference `ref`."""
    url = "http://export.arxiv.org/api/query?id_list=" + ref
    xml_data = urlopen(url).read().decode("utf-8")
    data = xmltodict.parse(xml_data)["feed"]["entry"]

    if isinstance(data["author"], list):
        authors = [auth["name"] for auth in data["author"]]
    else:
        authors = [data["author"]["name"]]

    string_format = lambda s: s.replace("\r", "").replace("\n", "").replace("  ", " ")
    dic = {
        "id": data["id"],
        "title": string_format(data["title"]),
        "authors": authors,
        "category": data["arxiv:primary_category"]["@term"],
    }

    return dic


def list_to_string(lst):
    """Takes a list of items (strings) and returns a string of items separated
    by semicolons.
    e.g.
        list_to_string(['John', 'Alice'])
            #=> 'John; Alice'
    """
    return "; ".join(lst)


def string_to_list(string):
    """Takes a string and splits into a list of strings separated by semicolons. In
    effect, the inverse operation of list_to_string().
    e.g.
        string_to_list('John; Alice')
            #=> ['John', 'Alice']
    """
    return string.split("; ")


def expand_tag(tag, dic):
    if tag[0] == "#":
        return dic[tag[1:]]

    return tag


def read_xarta_file():
    """Read database location from ~/.xarta file and returns path as string."""
    home = os.path.expanduser("~")

    try:
        with open(home + "/.xarta", "r") as xarta_file:
            return xarta_file.readline()
    except:
        raise Exception(f"Could not read {home}/.xarta")


def dots_if_needed(s, max_chars):
    """If string `s` is longer than `max_chars`, return an abbreviated string
    with ellipsis.
    e.g.
        dots_if_needed('This is a very long string.', 12)
            #=> 'This is a ve...'
    """
    if len(s) < max_chars:
        return s
    return s[: (max_chars - 3)] + "..."


def format_data_term(data, select=False):
    """Returns nicely formatted data wrt terminal dimensions."""
    _, term_columns = os.popen("stty size", "r").read().split()

    # max chars in column = a fifth of the terminal window - 1 or so
    col_width = int(term_columns) // 5
    offset = 2 if select else 1  # offset b/c col_width still leads to spillage
    max_chars = col_width - offset

    short_data = []
    for row in data:
        short_row = [dots_if_needed(s, max_chars) for s in row]
        short_data.append(short_row)

    return short_data


def get_all_rows_from_db(path):
    query_command = f"""SELECT * FROM papers;"""

    conn = sqlite3.connect(path)
    c = conn.cursor()
    query_results = c.execute(query_command)
    all_rows = c.fetchall()
    c.close()

    return all_rows
