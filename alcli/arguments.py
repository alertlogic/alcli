class CLIArgument(object):
    def __init__(self, name):
        self._name = name

    @property
    def cli_name(self):
        if self._positional_arg:
            return self._name
        else:
            return '--' + self._name

    def add_to_parser(self, parser):
        cli_name = self.cli_name

    def add_to_parser(self, parser):
        kwargs = {}
        parser.add_argument(cli_name, **kwargs)

    @property
    def name(self):
        return self._name
