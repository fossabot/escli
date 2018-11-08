import logging

from cliff.command import Command
from escli.settings import ClusterSettings


class LoggingGet(Command):
    """Get a logger value."""

    log = logging.getLogger(__name__)
    settings = ClusterSettings()

    def take_action(self, parsed_args):
        persistency = "transient"

        if parsed_args.persistent:
            persistency = "persistent"

        self.log.debug('Persistency is ' + persistency)

        if not parsed_args.logger.startswith('logger'):
            parsed_args.logger = 'logger.' + parsed_args.logger

        level = self.settings.get(
            parsed_args.logger,
            persistency=persistency
        ) or ''

        self.log.info(
            '{} : {}'
            .format(str(parsed_args.logger), str(level))
        )

    def get_parser(self, prog_name):
        parser = super(LoggingGet, self).get_parser(prog_name)
        parser.add_argument(
            "logger",
            metavar="<logger>",
            help=("Logger to get value"),
        )
        persistency_group = parser.add_mutually_exclusive_group()
        persistency_group.add_argument(
            "--transient",
            action="store_true",
            help=("Set setting as transient (default)")
        )
        persistency_group.add_argument(
            "--persistent",
            action="store_true",
            help=("Set setting as persistent")
        )
        return parser


class LoggingReset(Command):
    """Reset a logger value."""

    log = logging.getLogger(__name__)
    setting = ClusterSettings()

    def take_action(self, parsed_args):
        persistency = "transient"

        if parsed_args.persistent:
            persistency = "persistent"

        self.log.debug('Persistency is ' + persistency)

        if not parsed_args.logger.startswith('logger'):
            parsed_args.logger = 'logger.' + parsed_args.logger

        self.log.info(
            'Resetting logger {}'
            .format(parsed_args.logger)
        )
        self.setting.set(
            parsed_args.logger,
            None,
            persistency=persistency
        )

    def get_parser(self, prog_name):
        parser = super(LoggingReset, self).get_parser(prog_name)
        parser.add_argument(
            "logger",
            metavar="<logger>",
            help=("Logger to set"),
        )
        persistency_group = parser.add_mutually_exclusive_group()
        persistency_group.add_argument(
            "--transient",
            action="store_true",
            help=("Set setting as transient (default)")
        )
        persistency_group.add_argument(
            "--persistent",
            action="store_true",
            help=("Set setting as persistent")
        )
        return parser


class LoggingSet(Command):
    """Set a logger value."""

    log = logging.getLogger(__name__)
    setting = ClusterSettings()

    def take_action(self, parsed_args):
        persistency = "transient"

        if parsed_args.persistent:
            persistency = "persistent"

        self.log.debug('Persistency is ' + persistency)

        if not parsed_args.logger.startswith('logger'):
            parsed_args.logger = 'logger.' + parsed_args.logger

        self.log.info(
            'Changing logger {} to {}'
            .format(parsed_args.logger, parsed_args.level)
        )

        self.setting.set(
            parsed_args.logger,
            parsed_args.level,
            persistency=persistency
        )

    def get_parser(self, prog_name):
        parser = super(LoggingSet, self).get_parser(prog_name)
        parser.add_argument(
            "logger",
            metavar="<logger>",
            help=("Logger to set"),
        )
        parser.add_argument(
            "level",
            metavar="<level>",
            help=("Log level"),
            choices=['TRACE', 'DEBUG', 'INFO', 'WARN']
        )
        persistency_group = parser.add_mutually_exclusive_group()
        persistency_group.add_argument(
            "--transient",
            action="store_true",
            help=("Set setting as transient (default)")
        )
        persistency_group.add_argument(
            "--persistent",
            action="store_true",
            help=("Set setting as persistent")
        )
        return parser
