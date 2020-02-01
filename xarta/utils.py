"""Some useful functions."""

from sys import platform
from urllib.request import urlopen
import os
import re
import xmltodict


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


class XartaError(Exception):
    """Custom Exception class. Used in a try/catch statement to distinguish between
    'expected' errors (from a raise command) and unexpected errors"""

    pass


if platform.startswith("linux"):
    OPEN_COMMAND = "xdg-open "
elif platform.startswith("darwin"):
    OPEN_COMMAND = "open "
else:
    raise XartaError("Xarta is currently not supported on Windows.")


def is_arxiv_category(s):
    """Returns true if the string s is an arxiv category."""
    return s in ARXIV_CATEGORIES


def is_valid_ref(ref):
    """Returns True if s is a valid arXiv reference."""
    is_new_arxiv_ref = bool(re.match("\d{4}\.\d+", ref))
    is_old_arxiv_ref = bool(re.match("[\w\-\.]+\/\d+", ref))
    return is_new_arxiv_ref or is_old_arxiv_ref or is_arxiv_category(ref)


def process_ref(paper_id, verbose=True):
    # strip version
    proc_paper_id = re.sub("v[0-9]+$", "", paper_id)
    if proc_paper_id != paper_id and verbose:
        print("Stripping version from paper ID.")

    # remove leading arxiv, i.e., such that paper_id='    arXiv: 2001.1234' is still valid
    paper_id = proc_paper_id
    proc_paper_id = re.sub("^\s*arxiv[:\- ]", "", paper_id, flags=re.IGNORECASE)
    if proc_paper_id != paper_id and verbose:
        match = re.search("^\s*arxiv[:\- ]", paper_id, flags=re.IGNORECASE)[0]
        print("Stripping leading '" + match + "'.")

    return proc_paper_id


def arxiv_open(ref, pdf=False):
    """Opens arxiv ref in browser."""

    if is_arxiv_category(ref):
        os.system(OPEN_COMMAND + " https://arxiv.org/list/" + ref + "/new")
    elif pdf:
        os.system(OPEN_COMMAND + " https://arxiv.org/pdf/" + ref + ".pdf")
    else:
        os.system(OPEN_COMMAND + " https://arxiv.org/abs/" + ref)


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


def check_filter_is_sanitary(filter_, keywords):
    """Check if a filter is (mostly) safe for evaluating. If it is not, raise an
    error explaining why."""
    if ";" in filter_:
        raise XartaError("Filter must not contain semicolons.")
    if "." in filter_:
        raise XartaError("Filter must not contain periods.")
    if "()" in filter_:
        raise XartaError("Filter must not contain function calls.")
    if "__import__" in filter_:
        raise XartaError("Filter must not contain '__import__'.")

    # follow up tests, is it of the form we expect: '\w+' in KEYWORD this basic
    # form can be sorrounded with brackets and connected by 'or' and 'and'
    # statements. so if we create a regexp for this expression, delete matches,
    # and then remove 'or' and 'and' statements we should be left with an empty
    # string. Or it is an invalid filter

    # allow keywords to be capitalised, as users may write them as they appear
    # in the table header
    keywords += [key.capitalize() for key in keywords]

    # create regexp
    regex_base = r"""[\(\s]*['"][\w\-\. ]+['"](in|not|\s)*("""
    for keyword in keywords:
        regex_base += keyword + "|"
    regex_base = regex_base.strip("|") + r")[\s\)]*"

    # look for instances of regex_base
    tmp = filter_
    while re.search(regex_base, tmp):
        tmp = re.sub(regex_base, "", tmp)

    # new remove instances of logic keywords
    regex_logic = r"""[\s\(\)]*(and|or|not|\s)+[\s\(\)]*"""
    while re.search(regex_logic, tmp):
        tmp = re.sub(regex_logic, "", tmp)

    if tmp.strip():
        raise XartaError("Filter does not look like an expected python logic string.")

    # note that this still lets through clearly wrong strings like filter_='and'.


# As far as I can tell, this is used to generate tags using information from the arxiv. e.g., #title would expand to the title of the paper.
# Currently, all of the information that could be expanded like this (id,title,authors,category) is ALREADY added to the database. Generating such tags seems useless?
# def expand_tag(tag, dic):
#     breakpoint()
#     if tag[0] == "#":
#         return dic[tag[1:]]

#     return tag


def dots_if_needed(s, max_chars):
    """If string `s` is longer than `max_chars`, return an abbreviated string
    with ellipsis.
    e.g.
        dots_if_needed('This is a very long string.', 12)
            #=> 'This is a ve...'
    """
    if s is None or len(s) < max_chars:
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


def process_and_validate_ref(ref, paper_database):
    """Takes a reference and database, resolves aliases, and processes arxiv
    references. Returns the processed reference or throws an error if it is not a
    valid reference. """

    # if ref is not defined (as is the case for optional arguments), just return ref
    if not ref:
        return ref

    processed_ref = paper_database.resolve_alias(ref) or ref
    processed_ref = process_ref(processed_ref)
    if not is_valid_ref(processed_ref):
        raise XartaError("Not a valid arXiv reference or alias: " + ref)
    return processed_ref
