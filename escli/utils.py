import logging
import os
import yaml
import sys

from cliff.lister import Lister


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class JSONFormatter:
    """docstring for JSONFormatter."""

    def __init__(self, json):
        super(JSONFormatter, self).__init__()
        self.json = json

    def _create_column_name_from_key(self, tup):
        column_name = ''

        if len(tup) == 1:
            column_name = tup[0]
            if '.' in column_name:
                column_name = column_name.replace('.', ' ')
            if '_' in column_name:
                column_name = column_name.replace('_', ' ')

            column_name = column_name.title()
        else:
            column_name = tup[1]

        return column_name

    def _ensure_params_format(self, raw_list):
        valid_list = []

        for element in raw_list:
            if isinstance(element, str):
                element = (element,)
            valid_list.append((
                element[0],
                self._create_column_name_from_key(element)
            ))

        return tuple(valid_list)

    def to_lister(self, columns=[]):

        columns = self._ensure_params_format(columns)

        headers = []
        for element in columns:
            headers.append(element[1])
        headers = tuple(headers)

        lst = []
        for obj in self.json:
            row = []
            for element in columns:
                row.append(obj.get(element[0]))
            lst.append(tuple(row))

        return (
            headers,
            tuple(lst)
        )

    def to_show_one(self, lines=[]):
        lines = self._ensure_params_format(lines)

        keys = []
        values = []

        for line in lines:
            keys.append(line[1])
            values.append(self.json.get(line[0]))

        return (tuple(keys), tuple(values))


class Context:
    """docstring for Context."""

    def __init__(self, name, **kwargs):
        super(Context, self).__init__()
        self.LOG = logging.getLogger(__name__)
        self.name = name

        for key, value in kwargs.items():
            setattr(self, key, value)


class ConfigFileParser:
    """docstring for ConfigFileParser."""

    log = logging.getLogger(__name__)

    def __init__(self):
        super(ConfigFileParser, self).__init__()
        self.path = os.path.expanduser("~") + '/.esclirc'
        self.log.debug('Trying to load config file : {}'.format(self.path))

    def load_configuration(self):
        self.log.debug('Loading configuration...')
        config_blocks = [
            'clusters',
            'contexts',
            'default-context',
            'settings',
            'users'
        ]

        with open(self.path, 'r') as config_file:
            try:
                self.raw = yaml.safe_load(config_file)
            except yaml.YAMLError as err:
                self.log.critical('Cannot read YAML from ' + self.path)
                self.log.critical(str(err.problem) + str(err.problem_mark))
                sys.exit(1)

        for config_block in config_blocks:
            if not hasattr(self, config_block):
                setattr(self, config_block, None)
            self.load_config_block(config_block)
            self.log.debug('{}: {}'.format(
                config_block,
                getattr(self, config_block)
            ))

    def load_config_block(self, key):
        if key in self.raw:
            setattr(self, key, self.raw.get(key))
        else:
            self.log.debug('Cannot find config block : ' + key)

    def get_context_informations(self, context_name):
        user = self.users.get(self.contexts.get(context_name).get('user'))
        cluster = self.clusters.get(
            self.contexts.get(context_name).get('cluster')
        )

        return Context(context_name, user=user, cluster=cluster)


class EscliLister(Lister):
    """docstring for EscliLister."""

    def get_parser(self, prog_name):
        parser = super(EscliLister, self).get_parser(prog_name)
        group = self._formatter_group
        group.add_argument(
            '-a',
            '--attribute',
            help="specify the attribute(s) to include (comma separated)."
        )
        return parser

    def get_by_attribute_name(self, attribute, data):
        attribute = attribute.split(',')
        data = dict((k, v) for k, v in data)
        return tuple([(attr, data.get(attr)) for attr in attribute])

    def run(self, parsed_args):
        parsed_args = self._run_before_hooks(parsed_args)
        self.formatter = self._formatter_plugins[parsed_args.formatter].obj
        column_names, data = self.take_action(parsed_args)

        if 'attribute' in parsed_args and parsed_args.attribute is not None:
            data = self.get_by_attribute_name(parsed_args.attribute, data)

        column_names, data = self._run_after_hooks(parsed_args,
                                                   (column_names, data))
        self.produce_output(parsed_args, column_names, data)
        return 0


def print_success(message):
    print("{}{}{} {}".format(
        Color.GREEN,
        'SUCCESS',
        Color.END,
        message
    ))


def print_output(message):
    print("{}".format(
        message
    ))


def flatten_dict(dictionary):
    def expand(key, value):
        if isinstance(value, dict):
            return [
                (key + '.' + k, v)
                for k, v in flatten_dict(value).items()
            ]
        else:
            return [(key, value)]

    items = [item for k, v in dictionary.items() for item in expand(k, v)]

    return dict(items)

def colorize(str, color):
    return "{}{}{}".format(
        color,
        str,
        Color.END
    )
