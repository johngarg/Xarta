"""Some useful functions."""

from sys import platform
from urllib.request import urlopen
import os
import re
import xmltodict


# get the home directory
HOME = os.path.expanduser("~")

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


def check_filter_is_sanitary(filter_, keywords_tmp):
    """Check if a filter is (mostly) safe for evaluating. If it is not, raise an
    error explaining why."""

    # firstly, avoid side effects.
    keywords = keywords_tmp.copy()

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

    # note that this check  still lets through clearly wrong strings like filter_='and'.
    # this will raise an error but should never be harmfull


def dots_if_needed(s, max_chars):
    """If string `s` is longer than `max_chars`, return an abbreviated string
    with ellipsis.
    e.g.
        dots_if_needed('This is a very long string.', 12)
            #=> 'This is a ve...'
    """
    if s is None or len(s) <= max_chars:
        return s
    return s[: (max_chars - 3)] + "..."


def format_data_term(data, headers, select=False, reference_prefix=""):
    """Returns nicely formatted data wrt terminal dimensions."""

    _, term_columns = os.popen("stty size", "r").read().split()
    term_columns = int(term_columns)
    headers = [head.capitalize() for head in headers]

    if term_columns < 120:
        # remove category column
        i = headers.index("Category")
        data = [row[:i] + row[i + 1 :] for row in data]
        headers = headers[:i] + headers[i + 1 :]
    if term_columns < 100:
        # remove alias column
        i = headers.index("Alias")
        data = [row[:i] + row[i + 1 :] for row in data]
        headers = headers[:i] + headers[i + 1 :]

    # max chars allowed in all columns combined is given by terminal size with a
    # small ofset ammount for spacing between columns
    ncols = len(headers)
    available_space = term_columns
    available_space -= (ncols - 1) * 2

    digits_offset = 0
    if select:
        # selection column is also present
        digits_offset = len(str(len(data))) + 2
        available_space -= digits_offset

    # next intelligently assign horizontal spacing to columns. Cap each columns
    # space to at most a fair fraction of the REMAINING space. Note that this
    # means the order in which spacing is asigned matters. For example, if we
    # had one "long" column with a lot of text and and 2 very short columns, if
    # we processed the long column first it could take up at most 1/3 of the
    # screen, but if we process it last it could take up 1-2*epsilon of the
    # screen. Thus, process lowes priority / space needed columns first.
    ascending_expected_size = ["Category", "Ref", "Alias", "Authors", "Tags", "Title"]
    column_sizes = [0] * len(headers)
    for head in ascending_expected_size:
        if head not in headers:
            # already removed due to size restrictions
            continue

        # what index does this column refer to?
        index = headers.index(head)

        # current 'fair fraction':
        available_column_space = available_space // ncols

        # is there still space left?
        if available_column_space < len(head):
            raise XartaError("Error: Terminal is too small to print table.")

        # to figure out how much space the column "wants", find longest member
        # of column.
        data_length = [len(row[index]) for row in data]
        desired_space = max(data_length + [len(head)])

        # how much space is actually used by the column
        column_sizes[index] = min(desired_space, available_column_space)

        # restric space left
        available_space -= column_sizes[index]
        ncols -= 1

    short_data = []
    for row in data:
        short_row = [
            dots_if_needed(s, max_chars) for s, max_chars in zip(row, column_sizes)
        ]
        short_data.append(short_row)

    # append optional reference prefixes, and convert reference to a secret string
    short_data = [
        [SecretString(reference_prefix + row[0]), *row[1:]] for row in short_data
    ]

    return short_data, headers, column_sizes, digits_offset


class SecretString:
    """This is just a string. Tabulate looks for strings that look like numbers and
    formates them as floats, and there is no way to disable this. As we do not want
    to format our arxiv numbers, use SecretString as tabulate does not recognise it
    as a float.

    Alternatively we could have made tabulate left-align all floats and
    specified a float formatter. However the formatter needs to be "smart" and
    be able to differentiate between old and new arxiv mumbers. So this is much
    easier.
    """

    def __init__(self, string):
        self.string = string

    def __str__(self):
        return self.string


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


def write_database_path(database_path, config_path=HOME):
    """Write database location to a file, usually in HOME  """
    config_file = os.path.join(config_path, ".xarta")
    with open(config_file, "w") as xarta_file:
        xarta_file.write(database_path)
    print(f"Database location saved to {config_file}")


def read_database_path():
    """Read database location from a file, usually ~/.xarta, and return path as a string."""
    try:
        #Try get config file from enviromental variable: XARTACONFIG
        config_file=os.environ['XARTACONFIG']
    except:
        #varioable not defined, use default
        config_file = os.path.join(HOME, ".xarta")
    try:
        with open(config_file, "r") as xarta_file:
            return xarta_file.readline()
    except FileNotFoundError:
        return None


def print_table(data, headers, select):
    from tabulate import tabulate

    # This does not work for some reason, as a workaround use another character
    # in place of whitespace and replace just before printing the table
    # tabulate.PRESERVE_WHITESPACE = True
    whitespace_char = "~"

    # process data for printing (fit to screen)
    formatted_data, formatted_headers, column_sizes, offset = format_data_term(
        data, headers, select
    )

    hlines = ["-" * col_size for col_size in column_sizes]

    frontmatter = [formatted_headers, hlines]
    for row in frontmatter:
        row[0] = whitespace_char * offset + row[0]

    print(tabulate(frontmatter, tablefmt="plain").replace(whitespace_char, " "))
    print(tabulate(formatted_data, tablefmt="plain", showindex=select))
