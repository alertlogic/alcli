import argparse
from difflib import get_close_matches

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


class CommandAction(argparse.Action):
    def __init__(self, option_strings, dest, command_table, **kwargs):
        self.command_table = command_table
        super(CommandAction, self).__init__(
            option_strings, dest, choices=self.choices, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

    @property
    def choices(self):
        return list(self.command_table.keys())

    @choices.setter
    def choices(self, val):
        # argparse.Action will always try to set this value upon
        # instantiation, but this value should be dynamically
        # generated from the command table keys. So make this a
        # NOOP if argparse.Action tries to set this value.
        pass


class CLIArgParser(argparse.ArgumentParser):
    Formatter = argparse.RawTextHelpFormatter

    # Number of choices per line
    ChoicesPerLine = 2

    def _check_value(self, action, value):
        # converted value must be one of the choices (if specified)
        if action.choices is not None and value not in action.choices:
            msg = ['Invalid choice, valid choices are:\n']
            for i in range(len(action.choices))[::self.ChoicesPerLine]:
                current = []
                for choice in action.choices[i:i+self.ChoicesPerLine]:
                    current.append('%-40s' % choice)
                msg.append(' | '.join(current))
            possible = get_close_matches(value, action.choices, cutoff=0.8)
            if possible:
                extra = ['\n\nInvalid choice: %r, maybe you meant:\n' % value]
                for word in possible:
                    extra.append('  * %s' % word)
                msg.extend(extra)
            raise argparse.ArgumentError(action, '\n'.join(msg))

    def __init__(self, command_table, version_string,
                 description, argument_table, prog=None):
        super(CLIArgParser, self).__init__(
            formatter_class=self.Formatter,
            add_help=False,
            conflict_handler='resolve',
            description=description,
            usage=USAGE,
            prog=prog)
        self._build(command_table, version_string, argument_table)

    def parse_known_args(self, args, namespace=None):
        parsed, remaining = super(CLIArgParser, self).parse_known_args(
                                                            args, namespace)
        return parsed, remaining

    def _build(self, command_table, version_string, argument_table):
        self.add_argument('--version', action="version",
                          version=version_string,
                          help='Display the version of this tool')
        self.add_argument('--profile', action="store",
                          help="Specify cnfiguration profile name to use")
        self.add_argument('command', action=CommandAction,
                          command_table=command_table)
