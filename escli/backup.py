import logging

from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne
from escli.main import Escli
from escli.utils import Color, JSONFormatter, print_output, colorize


class RepositoryList(Lister):
    """List repositories."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        repositories = Escli._es.cat.repositories(format="json")
        json_formatter = JSONFormatter(repositories)
        return json_formatter.to_lister(columns=[
            ('id'),
            ('type'),
        ])


class RepositoryShow(ShowOne):
    """Display repository details."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        repository = Escli._es.snapshot.get_repository(
            repository=parsed_args.repository,
            format="json"
        ).get(parsed_args.repository)
        json_formatter = JSONFormatter(repository)
        return json_formatter.to_show_one(lines=[
            ('type'),
            ('settings'),
        ])

    def get_parser(self, prog_name):
        parser = super(RepositoryShow, self).get_parser(prog_name)
        parser.add_argument(
            "repository",
            metavar="<repository>",
            help=("Repository get details")
        )
        return parser


class RepositoryVerify(Command):
    """Verify repository status."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        repository = Escli._es.snapshot.verify_repository(
            repository=parsed_args.repository,
            format="json"
        )
        self.log.warn('Pretty display is currently not implemented')
        print(repository)

    def get_parser(self, prog_name):
        parser = super(RepositoryVerify, self).get_parser(prog_name)
        parser.add_argument(
            "repository",
            metavar="<repository>",
            help=("Repository get details")
        )
        return parser


class SnapshotCreate(Command):
    """Create a snapshot."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        status = Escli._es.snapshot.create(
            repository=parsed_args.repository,
            snapshot=parsed_args.name,
            body=self.build_body(parsed_args)
        )

        print_output(status.get('accepted'))

    def build_body(self, parsed_args):
        return {
            'ignore_unavailable': parsed_args.ignore_unavailable,
            'include_global_state': parsed_args.include_global_state
        }

    def get_parser(self, prog_name):
        parser = super(SnapshotCreate, self).get_parser(prog_name)
        parser.add_argument(
            '--ignore-unavailable',
            action='store',
            help='Setting it to true will cause indices that do not exist to be ignored during snapshot creation',
            choices=[True, False],
            required=False,
            default=False
        )
        parser.add_argument(
            '--include-global-state',
            action='store',
            help='Permit the cluster global state to be stored as part of the snapshot',
            required=False,
            choices=[True, False],
            default=True
        )
        parser.add_argument(
            '-r', '--repository',
            action='store',
            help='Repository',
            required=True
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help=("Name")
        )
        return parser


class SnapshotDelete(Command):
    """Delete a snapshot from a repository."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        ret = Escli._es.snapshot.delete(
            repository=parsed_args.repository,
            snapshot=parsed_args.snapshot,
            format="json"
        )
        print(ret)

    def get_parser(self, prog_name):
        parser = super(SnapshotDelete, self).get_parser(prog_name)
        parser.add_argument(
            '-r', '--repository',
            action='store',
            help='Repository',
            required=True
        )
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            help=("Snapshot to delete")
        )
        return parser


class SnapshotList(Lister):
    """List snapshots."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        snapshots = self.transform(Escli._es.cat.snapshots(
            repository=parsed_args.repository,
            format="json"
        ))
        json_formatter = JSONFormatter(snapshots)
        return json_formatter.to_lister(columns=[
            ('id'),
            ('status'),
            ('start_time'),
            ('end_time'),
            ('duration'),
            ('indices'),
            ('successful_shards'),
            ('failed_shards'),
            ('total_shards'),
        ])

    def transform(self, snapshots):
        for idx in range(len(snapshots)):
            if snapshots[idx].get('status') == 'PARTIAL':
                snapshots[idx]['status'] = colorize(
                    snapshots[idx].get('status'),
                    Color.YELLOW
                )
                snapshots[idx]['failed_shards'] = colorize(
                    snapshots[idx].get('failed_shards'),
                    Color.RED
                )
            elif snapshots[idx].get('status') == 'IN_PROGRESS':
                snapshots[idx]['status'] = colorize(
                    snapshots[idx].get('status'),
                    Color.CYAN
                )

        return snapshots

    def get_parser(self, prog_name):
        parser = super(SnapshotList, self).get_parser(prog_name)
        parser.add_argument(
            '-r', '--repository',
            action='store',
            help='Repository',
            required=True
        )
        return parser


class SnapshotRestore(Command):
    """Restore a snapshot."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        ret = Escli._es.snapshot.restore(
            repository=parsed_args.repository,
            snapshot=parsed_args.snapshot,
            format="json"
        )
        print(ret)

    def get_parser(self, prog_name):
        parser = super(SnapshotRestore, self).get_parser(prog_name)
        parser.add_argument(
            '-r', '--repository',
            action='store',
            help='Repository',
            required=True
        )
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            help=("Snapshot to restore")
        )
        return parser


class SnapshotShow(ShowOne):
    """Display snapshots details."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.snapshot = Escli._es.snapshot.get(
            repository=parsed_args.repository,
            snapshot=parsed_args.snapshot,
            format="json"
        ).get('snapshots')[0]

        self.transform()

        json_formatter = JSONFormatter(self.snapshot)
        return json_formatter.to_show_one(lines=[
            ('snapshot'),
            ('uuid', 'UUID'),
            ('version_id'),
            ('version'),
            ('indices'),
            ('state'),
            ('start_time'),
            ('end_time'),
            ('duration_in_millis', 'Duration (ms)'),
            ('failures'),
            ('total_shards'),
            ('failed_shards'),
            ('successful_shards'),
        ])

    def transform(self):
        # Transform shard's dict into 3 separate values
        self.snapshot['indices'] = ', '.join(self.snapshot['indices'])
        self.snapshot['total_shards'] = self.snapshot\
            .get('shards').get('total')

        self.snapshot['successful_shards'] = self.snapshot\
            .get('shards').get('successful')

        failed_shards = int(self.snapshot.get('shards').get('failed'))
        if failed_shards > 0:
            failed_shards = Color.RED + str(failed_shards) + Color.END

        self.snapshot['failed_shards'] = failed_shards

        # Show failures as human-friendly text
        if len(self.snapshot['failures']) > 0:
            failures_message = ''
            for failure in self.snapshot['failures']:
                failure_message = "{}[{}] - {}: {}"\
                    .format(
                        failure.get('index'),
                        failure.get('shard_id'),
                        failure.get('status'),
                        failure.get('reason')
                    )
                failures_message = failures_message + '\n' + failure_message

            self.snapshot['failures'] = failures_message + '\n'
        else:
            self.snapshot['failures'] = '0'

        # Add color to snapshot's state
        if self.snapshot['state'] == 'SUCCESS':
            self.snapshot['state'] = "{}{}{}".format(
                Color.GREEN,
                self.snapshot['state'],
                Color.END
            )
        elif self.snapshot['state'] == 'PARTIAL':
            self.snapshot['state'] = "{}{}{}".format(
                Color.YELLOW,
                self.snapshot['state'],
                Color.END
            )

    def get_parser(self, prog_name):
        parser = super(SnapshotShow, self).get_parser(prog_name)
        parser.add_argument(
            '-r', '--repository',
            action='store',
            help='Repository',
            required=True
        )
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            help=("Snapshot to get details")
        )
        return parser
