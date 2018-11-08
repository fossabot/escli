import logging

from cliff.command import Command
from escli.main import Escli


class ClusterRerouteRetry(Command):
    """Try again to reroute failed shards."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        Escli._es.cluster.reroute(retry_failed=True)
