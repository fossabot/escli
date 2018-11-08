import logging
import sys

from cliff.command import Command
from escli.main import Escli


class QuerySearch(Command):
    """Execute a search query from stdin."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        input = sys.stdin.read()
        ret = Escli._es.search(index=parsed_args.index, body=input)
        print(ret)

    def get_parser(self, prog_name):
        parser = super(QuerySearch, self).get_parser(prog_name)
        parser.add_argument(
            '-i', '--index',
            action='store',
            required=False,
            default='_all',
            help=("A comma-separated list of index names to search; use '_all'"
                    " to perform the operation on all indices")
        )

        return parser
