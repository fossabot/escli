import logging

from cliff.lister import Lister
from cliff.command import Command
from escli.settings import IndexSettings
from escli.main import Escli
from escli.utils import JSONFormatter, print_output


class IndexCreate(Command):
    """Create an index."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info(
            'Creating index {} with {} shards and {} replicas'.format(
                parsed_args.index,
                0,
                0
            )
        )
        Escli._es.indices.create(index=parsed_args.index)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index to create"),
        )
        return parser


class IndexList(Lister):
    """List all indices."""

    log = logging.getLogger(__name__)
    settings = IndexSettings()

    def take_action(self, parsed_args):
        indices = Escli._es.cat.indices(format='json')
        json_formatter = JSONFormatter(indices)
        return json_formatter.to_lister(columns=[
            ('index'),
            ('health',),
            ('status'),
            ('uuid', 'UUID'),
            ('pri', 'Primary'),
            ('rep', 'Replica'),
            ('docs.count'),
            ('docs.deleted'),
            ('store.size'),
            ('pri.store.size', 'Primary Store Size')
        ])


class IndexClose(Command):
    """Close an index."""

    log = logging.getLogger(__name__)
    settings = IndexSettings()

    def take_action(self, parsed_args):
        self.log.info('Closing index ' + parsed_args.index)
        Escli._es.indices.close(index=parsed_args.index)

    def get_parser(self, prog_name):
        parser = super(IndexClose, self).get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index to close"),
        )
        return parser


class IndexDelete(Command):
    """Delete an index."""

    log = logging.getLogger(__name__)
    settings = IndexSettings()

    def take_action(self, parsed_args):
        self.log.info('Deleting index ' + parsed_args.index)
        Escli._es.indices.delete(index=parsed_args.index)

    def get_parser(self, prog_name):
        parser = super(IndexDelete, self).get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index to delete"),
        )
        return parser


class IndexOpen(Command):
    """Open an index."""

    log = logging.getLogger(__name__)
    settings = IndexSettings()

    def take_action(self, parsed_args):
        self.log.info('Opening index ' + parsed_args.index)
        Escli._es.indices.open(index=parsed_args.index)

    def get_parser(self, prog_name):
        parser = super(IndexOpen, self).get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index to close"),
        )
        return parser


class IndexSettingsGet(Command):
    """Retrieve an index setting."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.settings = IndexSettings(parsed_args.index)

        for index_settings in self.settings.get(parsed_args.setting):
            print_output("[{}] {} : {}".format(
                index_settings.index,
                parsed_args.setting,
                index_settings.value
            ))

    def get_parser(self, prog_name):
        parser = super(IndexSettingsGet, self).get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index")
        )
        parser.add_argument(
            "setting",
            metavar="<setting>",
            help=("Setting to get value")
        )
        return parser


class IndexSettingsReset(Command):
    """Reset a index setting."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info(
            'Resetting setting {}'
            .format(parsed_args.setting)
        )

        self.settings = IndexSettings(parsed_args.index)

        self.settings.set(
            parsed_args.setting,
            None,
        )

    def get_parser(self, prog_name):
        parser = super(IndexSettingsReset, self).get_parser(prog_name)
        parser.add_argument(
            "setting",
            metavar="<setting>",
            help=("Setting to reset")
        )
        return parser


class IndexSettingsSet(Command):
    """Set a index setting."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info(
            'Changing setting {} to {} in index {}'
            .format(parsed_args.setting, parsed_args.value, parsed_args.index)
        )

        self.settings = IndexSettings(parsed_args.index)

        self.settings.set(
            parsed_args.setting,
            parsed_args.value,
        )

    def get_parser(self, prog_name):
        parser = super(IndexSettingsSet, self).get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index")
        )
        parser.add_argument(
            "setting",
            metavar="<setting>",
            help=("Setting to set")
        )
        parser.add_argument(
            "value",
            metavar="<value>",
            help=("Value")
        )
        return parser


class IndexSlowlogThreshold(Command):
    """Change index slowlog threshold level."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('Threshold index ' + parsed_args.index)
        # Escli._es.indices.delete(index=parsed_args.index)
        self.index_settings = IndexSettings(parsed_args.index)

        if parsed_args.type == 'search':
            subtype = parsed_args.search_type
        elif parsed_args.type == 'indexing':
            subtype = 'index'

        if parsed_args.value:
            print('index.' + parsed_args.type + '.slowlog.threshold.'
                  + subtype + '.' + parsed_args.level, parsed_args.value)
        else:
            print('fooooo')

    def get_parser(self, prog_name):
        parser = super(IndexSlowlogThreshold, self).get_parser(prog_name)
        parser.add_argument(
            "index",
            metavar="<index>",
            help=("Index to act on"),
        )
        parser.add_argument(
            '-t', '--type',
            action='store',
            help='Slowlog type (one of: indexing, search)',
            choices=['indexing', 'search'],
            required=True
        )
        parser.add_argument(
            '-s', '--search-type',
            action='store',
            help='Search type',
            choices=['query', 'fetch'],
        )
        parser.add_argument(
            '-l', '--level',
            action='store',
            help='Log level',
            choices=['trace', 'debug', 'info', 'warn'],
            required=True
        )
        parser.add_argument(
            "value",
            metavar="<value>",
            help=("Value"),
            nargs='?'
        )
        return parser
