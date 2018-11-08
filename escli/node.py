import logging
import sys

from cliff.command import Command
from cliff.lister import Lister
from escli.main import Escli
from escli.utils import JSONFormatter
from escli.settings import ClusterSettings


class NodeDecommission(Command):
    """Decommission a node."""

    log = logging.getLogger(__name__)
    settings = ClusterSettings()

    def take_action(self, parsed_args):
        currently_excluded_nodes = self.settings.get(
            'cluster.routing.allocation.exclude._name',
            persistency='transient'
        )

        if parsed_args.name:
            if currently_excluded_nodes is None or \
               currently_excluded_nodes is "" or \
               len(currently_excluded_nodes) == 0:
                currently_excluded_nodes = parsed_args.name
            else:
                if len(currently_excluded_nodes) > 0 and \
                        parsed_args.name in currently_excluded_nodes:
                    self.log.info(
                        "Aborting, {} is already in list : {}"
                        .format(parsed_args.name, currently_excluded_nodes)
                    )
                    sys.exit()
                else:
                    currently_excluded_nodes = ','.join(
                        [currently_excluded_nodes + ',' + parsed_args.name])

            self.log.debug(currently_excluded_nodes)

            self.log.info('Decommissioning ' + parsed_args.name)
            self.settings.set(
                "cluster.routing.allocation.exclude._name",
                currently_excluded_nodes,
                persistency="transient"
            )
        else:
            self.log.info(currently_excluded_nodes)

    def get_parser(self, prog_name):
        parser = super(NodeDecommission, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=("Node name"),
            nargs='?'
        )
        return parser


class NodeHotThreads(Command):
    """Print hot threads on each nodes."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        print(Escli._es.nodes.hot_threads(type=parsed_args.type))

    def get_parser(self, prog_name):
        parser = super(NodeHotThreads, self).get_parser(prog_name)
        parser.add_argument(
            "type",
            metavar="<type>",
            help=("Type"),
            choices=['cpu', 'wait', 'block'],
            default='cpu',
            nargs='?'
        )
        return parser


class NodeRecommission(Command):
    """Recommission a node."""

    log = logging.getLogger(__name__)
    settings = ClusterSettings()

    def take_action(self, parsed_args):
        currently_excluded_nodes = self.settings.get(
            'cluster.routing.allocation.exclude._name',
            persistency='transient'
        ).split(',')

        try:
            currently_excluded_nodes.remove(parsed_args.name)
            currently_excluded_nodes = ','.join(currently_excluded_nodes)
            self.log.info('Recommissioning ' + parsed_args.name)
            self.settings.set(
                "cluster.routing.allocation.exclude._name",
                currently_excluded_nodes,
                persistency="transient"
            )
        except ValueError:
            self.log.info(parsed_args.name + " is already commissioned")

    def get_parser(self, prog_name):
        parser = super(NodeRecommission, self).get_parser(prog_name)
        parser.add_argument("name", metavar="<name>", help=("Node name"))
        return parser


class NodeList(Lister):
    """List nodes."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        nodes = Escli._es.cat.nodes(format='json')

        json_formatter = JSONFormatter(nodes)
        return json_formatter.to_lister(columns=[
            ('ip', 'IP'),
            ('heap.percent', 'Heap %'),
            ('ram.percent', 'RAM %'),
            ('cpu'),
            ('load_1m'),
            ('load_5m'),
            ('load_15m'),
            ('node.role', 'Role'),
            ('master'),
            ('name')
        ])
