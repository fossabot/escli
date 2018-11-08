import logging

from cliff.command import Command
from cliff.lister import Lister
from escli.main import Escli
from escli.utils import JSONFormatter


class AliasCreate(Command):
    """Create an alias."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info(
            'Creating alias {} on index {}'.format(
                parsed_args.name,
                parsed_args.index
            )
        )
        Escli._es.indices.put_alias(
            index=parsed_args.index,
            name=parsed_args.name
        )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index name the alias should point to"),
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help=("Alias to create"),
        )
        return parser


class AliasDelete(Command):
    """Delete an alias."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info(
            'Deleting the alias {} from index {}'.format(
                parsed_args.name,
                parsed_args.index
            )
        )
        Escli._es.indices.delete_alias(
            index=parsed_args.index,
            name=parsed_args.name
        )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index name the alias should point to"),
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help=("Alias to create"),
        )
        return parser


class AliasList(Lister):
    """List all aliases."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        aliases = self.transform(
            parsed_args,
            Escli._es.cat.aliases(format='json')
        )
        json_formatter = JSONFormatter(aliases)
        columns = [
            ('alias', 'Aliases')
        ]

        if parsed_args.index is '_all':
            columns += [('index')]

        return json_formatter.to_lister(columns=columns)

    def transform(self, parsed_args, aliases):
        filtered_aliases = aliases

        if parsed_args.index is not '_all':
            filtered_aliases = [
                x for x in aliases if x.get('index') == parsed_args.index
            ]

        return filtered_aliases

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index"),
            default='_all',
            nargs='?'
        )

        return parser
