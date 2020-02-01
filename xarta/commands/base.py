"""The basic command class."""

from ..utils import read_database_path


class BaseCommand:
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.database_path = read_database_path()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError("You must implement the run() method yourself!")
