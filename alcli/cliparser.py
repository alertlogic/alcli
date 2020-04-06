import argparse
from difflib import get_close_matches
from almdrlib.client import OpenAPIKeyWord

HELP_MESSAGE = (
    "To see help text, you can run:\n"
    "\n"
    "  alcli help\n"
    "  alcli <command> help\n"
    "  alcli <command> <subcommand> help\n"
)
USAGE = (
    "alcli [options] <command> <subcommand> [<subcommand> ...] [parameters]\n"
    f"{HELP_MESSAGE}"
)


class CliHelpAction(argparse.Action):
    def __init__(self, option_strings, dest, formatter, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class CliArgParserBase(argparse.ArgumentParser):
    # Number of choices per line
    ChoicesPerLine = 2

    def _check_value(self, action, value):
        # converted value must be one of the choices (if specified)
        if isinstance(action.choices, dict):
            choices = list(action.choices.keys())
        else:
            choices = action.choices

        if choices is not None and value not in choices:
            if 'help' in choices:
                choices.remove('help')
            msg = ['Invalid choice, valid choices are:\n']
            for i in range(len(choices))[::self.ChoicesPerLine]:
                current = []
                for choice in choices[i:i+self.ChoicesPerLine]:
                    current.append('%-40s' % choice)
                msg.append(' | '.join(current))
            possible = get_close_matches(value, choices, cutoff=0.8)
            if possible:
                extra = ['\n\nInvalid choice: %r, maybe you meant:\n' % value]
                for word in possible:
                    extra.append('  * %s' % word)
                msg.extend(extra)
            raise argparse.ArgumentError(action, '\n'.join(msg))


class ALCliArgsParser(CliArgParserBase):
    """
        Main CLI Arguments Parser
    """

    def __init__(self, services, version, description, prog=None):
        super().__init__(
                formatter_class=argparse.RawTextHelpFormatter,
                add_help=False,
                conflict_handler='resolve',
                description=description,
                usage=USAGE,
                prog=prog)

        self.add_argument('--version', action="version",
                          version=version,
                          help='Display the version of this tool')

        # self.add_argument('help', action=CliHelpAction, formatter="1234")
        # self.add_argument('help')
        self._subparsers = self.add_subparsers(
                dest='service',
                title='service',
                parser_class=ServicesArgsParser,
                required=False)
        self._create_parsers(services)

    def parse_known_args(self, args=None, namespace=None):
        parsed_args, remaining = super().parse_known_args(args, namespace)
        return parsed_args, remaining

    #
    # For all know services, create a subparser
    #
    def _create_parsers(self, services):
        self._subparsers.add_parser('help', service=None)
        for name, service in services.items():
            self._subparsers.add_parser(name, service=service)


class ServicesArgsParser(CliArgParserBase):
    """
        Alert Logic Services Parser
    """

    def __init__(self, *args, **kwargs):
        self._service = kwargs.pop('service')
        super().__init__(
                formatter_class=argparse.RawTextHelpFormatter,
                add_help=False,
                conflict_handler='resolve',
                usage=USAGE)

    def parse_known_args(self, args=None, namespace=None):
        #
        # Get Service API Schema
        #
        if self._service is None:
            return super().parse_known_args(args, namespace)

        service_api = self._service.session.get_service_api(
                                service_name=self._service.name)

        self._required = True
        subparsers = self.add_subparsers(
                dest='operation',
                title="operation",
                required=True,
                parser_class=OperationArgsParser)

        #
        # Add subparsers for all service operations
        #
        for op_name, op_spec in service_api['operations'].items():
            subparsers.add_parser(op_name, spec=op_spec)

        #
        # Add help command
        #
        subparsers.add_parser('help', spec=None)
        return super().parse_known_args(args, namespace)


class OperationArgsParser(CliArgParserBase):
    """
        Alert Logic Service Operation Parser
    """
    def __init__(self, *args, **kwargs):
        self._spec = kwargs.pop('spec')
        super().__init__(
                formatter_class=argparse.RawTextHelpFormatter,
                add_help=False,
                conflict_handler='resolve',
                usage=USAGE)

    def parse_known_args(self, args=None, namespace=None):
        # Add Operation arguments to the parser
        if 'help' in args:
            self.add_argument('help')
            return super().parse_known_args(args, namespace)
        elif self._spec:
            for key, value in self._spec[OpenAPIKeyWord.PARAMETERS].items():
                self.add_argument(
                    f"--{key}", required=value.get(OpenAPIKeyWord.REQUIRED))

        return super().parse_known_args(args, namespace)
