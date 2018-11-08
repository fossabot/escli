import logging

from cliff.lister import Lister
from escli.main import Escli
from escli.utils import Color, JSONFormatter


class CatAllocation(Lister):
    """Show shard allocation.

    Provides a snapshot of how shards have located around the cluster and the
    state of disk usage.
    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        allocation = Escli._es.cat.allocation(format='json')

        allocation = self.transform(allocation)

        json_formatter = JSONFormatter(allocation)
        return json_formatter.to_lister(columns=[
            ('shards'),
            ('disk.indices'),
            ('disk.used'),
            ('disk.avail'),
            ('disk.total'),
            ('disk.percent', 'Disk %'),
            ('host'),
            ('ip', 'IP'),
            ('node'),
        ])

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def transform(self, allocation):
        nodes = []

        for node in allocation:
            if int(node.get('disk.percent')) > 90:
                node['disk.percent'] = "{}{}{}".format(
                    Color.RED,
                    node['disk.percent'],
                    Color.END
                )

            elif int(node.get('disk.percent')) > 75:
                node['disk.percent'] = "{}{}{}".format(
                    Color.YELLOW,
                    node['disk.percent'],
                    Color.END
                )

            nodes.append(node)

        return nodes


class CatShards(Lister):
    """Show a detailed view of what nodes contain which shards.

    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        shards = Escli._es.cat.shards(
            format='json',
            index=parsed_args.index,
            bytes=parsed_args.unit
        )

        json_formatter = JSONFormatter(shards)
        return json_formatter.to_lister(columns=[
            ('index'),
            ('shard', '#'),
            ('prirep', 'Primary/Replica'),
            ('state'),
            ('docs', 'Documents'),
            ('store', 'Size ({})'.format(parsed_args.unit)),
            ('node')
        ])

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '-i', '--index',
            action='store',
            help='A comma-separated list of index names to limit the returned information',
            required=False
        )
        parser.add_argument(
            '--unit',
            action='store',
            help='The unit in which to display byte values',
            required=False,
            choices=[
                'b', 'k', 'kb', 'm', 'mb',
                'g', 'gb', 't', 'tb', 'p', 'pb'
            ],
            default='mb'
        )
        return parser
