import logging
import sys
import pprint
import argparse
import pkg_resources
import urllib3
import warnings

from box import Box
import elasticsearch as elasticsearch
from cliff.app import App
from cliff.commandmanager import CommandManager

from escli import utils
from escli.interactive import InteractiveApp


class Escli(App):

    _es = elasticsearch.Elasticsearch()
    _pp = pprint.PrettyPrinter(indent=4)
    _config = utils.ConfigFileParser()

    def __init__(self):
        super(Escli, self).__init__(
            description=pkg_resources.require('Escli')[0].project_name,
            version=pkg_resources.require('Escli')[0].version,
            command_manager=CommandManager('escli'),
            deferred_help=True,
            interactive_app_factory=InteractiveApp
        )
        self.interactive_mode = False

    def configure_logging(self):
        """Create logging handlers for any log output.
        """
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        logging.getLogger('elasticsearch').setLevel(logging.WARNING)

        # Disable urllib's warnings
        # See https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
        urllib3.disable_warnings()

        # Set up logging to a file
        if self.options.log_file:
            file_handler = logging.FileHandler(
                filename=self.options.log_file,
            )
            formatter = logging.Formatter(self.LOG_FILE_MESSAGE_FORMAT)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Always send higher-level messages to the console via stderr
        console = logging.StreamHandler(self.stderr)
        console_level = {1: logging.WARNING,
                         2: logging.INFO,
                         3: logging.DEBUG,
                         }.get(self.options.verbose_level, logging.DEBUG)
        console.setLevel(console_level)

        elasticsearch_log_level = {
            1: logging.WARNING,
            2: logging.INFO,
            3: logging.DEBUG,
        }.get(self.options.verbose_level, logging.DEBUG)
        logging.getLogger('elasticsearch').setLevel(elasticsearch_log_level)

        logging.addLevelName(
            logging.DEBUG,
            "{}{}{}".format(
                utils.Color.END,
                logging.getLevelName(logging.DEBUG),
                utils.Color.END
            )
        )
        logging.addLevelName(
            logging.INFO,
            "{}{}{}".format(
                utils.Color.BLUE,
                logging.getLevelName(logging.INFO),
                utils.Color.END
            )
        )
        logging.addLevelName(
            logging.WARNING,
            "{}{}{}"
            .format(
                utils.Color.YELLOW,
                logging.getLevelName(logging.WARNING),
                utils.Color.END
            )
        )
        logging.addLevelName(
            logging.ERROR,
            "{}{}{}"
            .format(
                utils.Color.PURPLE,
                logging.getLevelName(logging.ERROR),
                utils.Color.END
            )
        )
        logging.addLevelName(
            logging.CRITICAL,
            "{}{}{}"
            .format(
                utils.Color.RED,
                logging.getLevelName(logging.CRITICAL),
                utils.Color.END
            )
        )
        formatter = logging.Formatter(
            '%(levelname)-8s ' + self.CONSOLE_MESSAGE_FORMAT
        )
        console.setFormatter(formatter)
        root_logger.addHandler(console)

        return

    def create_context(self):
        if self.options.username and self.options.password:
            self.LOG.debug(
                'Username and Passowrd are provided. Building custom context.')
            user = {
                'username': self.options.username,
                'password': self.options.password
            }
            cluster = {
                'servers': [self.options.elasticsearch]
            }
            self.context = utils.Context('custom', user=user, cluster=cluster)
        elif self.options.context:
            try:
                self.context = self._config.get_context_informations(
                    str(self.options.context)
                )
                self.LOG.debug('Using provided context : ' + self.context.name)
            except AttributeError:
                self.LOG.fatal('Cannot load provided context.')
                sys.exit(1)
        else:
            self.LOG.debug(
                'No username/password nor context provided. '
                'Using default context.'
            )
            try:
                self.context = self._config.get_context_informations(
                    self._config.__getattribute__('default-context')
                )
                self.LOG.debug('Using default context : ' + self.context.name)
            except AttributeError:
                self.LOG.debug(
                    'Building noauth context.'
                )
                user = {
                    'username': None,
                    'password': None
                }
                cluster = {
                    'servers': [self.options.elasticsearch]
                }
                self.context = utils.Context(
                    'noauth',
                    user=user,
                    cluster=cluster
                )

        if hasattr(self._config, 'settings') and self._config.settings is not None:
            self.context.settings = Box(self._config.settings)

    def find_scheme(self):
        scheme = 'https'

        if self.context.cluster.get('servers')[0].startswith('http'):
            scheme = self.context.cluster.get('servers')[0].split(':')[0]

        self.LOG.debug('Using {} scheme'.format(scheme))

        return scheme

    def initialize_app(self, argv):
        self._config.load_configuration()
        self.create_context()
        username = None
        password = None

        if self.context.user is not None:
            username = self.context.user.get('username')
            password = self.context.user.get('password')

        servers = self.context.cluster.get('servers')[0]

        http_auth = (username, password) \
            if username and password \
            else None

        if hasattr(self.context, 'settings') and \
                'no_check_certificate' in self.context.settings and \
                self.context.settings.no_check_certificate:
            with warnings.catch_warnings(record=True) as warning:
                self.LOG.debug(warning)
                Escli._es = elasticsearch.Elasticsearch(
                    servers,
                    http_auth=http_auth,
                    verify_certs=False,
                    scheme=self.find_scheme(),
                    max_retries=0
                )
        else:
            Escli._es = elasticsearch.Elasticsearch(
                servers,
                http_auth=http_auth,
                verify_certs=True,
                scheme=self.find_scheme(),
                max_retries=0
            )

    def prepare_to_run_command(self, cmd):
        pass

    def clean_up(self, cmd, result, err):
        if err:
            self.LOG.debug('got an error: %s', err)

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False,
            **argparse_kwargs
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
        )
        verbose_group = parser.add_mutually_exclusive_group()
        verbose_group.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )
        verbose_group.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='Suppress output except warnings and errors.',
        )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
        )
        if self.deferred_help:
            parser.add_argument(
                '-h', '--help',
                dest='deferred_help',
                action='store_true',
                help="Show help message and exit.",
            )
        else:
            parser.add_argument(
                '-h', '--help',
                action=HelpAction,
                nargs=0,
                default=self,  # tricky
                help="Show this help message and exit.",
            )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Show tracebacks on errors.',
        )

        parser.add_argument(
            '-e',
            '--elasticsearch',
            default="http://localhost:9200",
            action='store',
            help='The elasticsearch host you wish to connect too. '
            '(Default: localhost:9200)',
        )

        parser.add_argument(
            '-u', '--username',
            default=False,
            action='store',
            help='Username',
        )

        parser.add_argument(
            '-p', '--password',
            default=False,
            action='store',
            help='Password',
        )

        parser.add_argument(
            '--no-check-certificate',
            default=False,
            action='store_true',
            help='Disable SSL certificate verification',
        )

        parser.add_argument(
            '--port',
            default=443,
            action='store',
            help='Port',
        )

        parser.add_argument(
            '--context',
            action='store',
            help='Context to use',
        )

        return parser

def main(argv=sys.argv[1:]):
    escli = Escli()
    return escli.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
