import logging

from cliff.lister import Lister
from escli.main import Escli
from escli.utils import JSONFormatter


class ConfigContextList(Lister):
    """List all contexts."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        contexts = []

        for context_name, context_definition in Escli._config.contexts.items():
            contexts.append({
                'name': context_name,
                'user': context_definition.get('user'),
                'cluster': context_definition.get('cluster')
            })

        json_formatter = JSONFormatter(contexts)
        return json_formatter.to_lister(columns=[
            ('name'),
            ('user'),
            ('cluster'),
        ])
