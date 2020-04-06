#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import textwrap
from almdrlib.client import OpenAPIKeyWord


class FormatHelp:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    SECTION_BREAK = '\n'*2
    OPERATION_DESCIPTION_FOOTER = \
        "See 'alcli help' for descriptions of global parameters."


class ALCliHelpFormatter():
    def __init__(self,
                 width=80,
                 indent_increment=2):
        self._name = ""
        self._width = width
        self._indent_increment = indent_increment
        self._initial_indent = '\t'
        self._subsequent_indent = '\t'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def bold(self, msg):
        return f"{FormatHelp.BOLD}{msg}{FormatHelp.END}"

    def underline(self, msg):
        return f"{FormatHelp.UNDERLINE}{msg}{FormatHelp.END}"

    def wraptext(self, text):
        if text is None:
            return ""

        return [
            textwrap.fill(
                        text=f"{str}",
                        width=self._width - 6,  # Not sure why, but this seem
                                                # to align correctly
                        initial_indent=self._initial_indent,
                        subsequent_indent=self._subsequent_indent
                    )
            for str in text.splitlines()
        ]

    def make_header(self, name):
        title_name = name.upper() + "()"
        return '\n'.join([
            title_name + title_name.rjust(self._width - len(title_name)),
            FormatHelp.SECTION_BREAK,
            self.bold("NAME"),
            '\t' + name + ' - ' + '\n'
            ])

    def make_footer(self, name):
        footer_title = name.upper() + "()"
        fill_text = " " * (self._width - len(footer_title))
        return f"{fill_text}{footer_title}"

    def make_description(self, description):
        if not description:
            return ""
        result = [self.bold("DESCRIPTION")]
        result.extend(self.wraptext(description))
        return '\n'.join(result) + '\n'


class ALCliMainHelpFormatter(ALCliHelpFormatter):
    def __init__(self,
                 servcices,
                 width=80,
                 indent_increment=2):
        super().__init__(width, indent_increment)
        self._services = servcices
        self._name = "alcli"
        self._description = (
            "The Alert Logic Command  Line  Interface is a tool "
            "to help you manage Alert Logic Services."
            )

    def make_synopsis(self):
        command = "\talcli [options] <command> <subcommand> [parameters]"
        description = (
            f"Use {self.underline('alcli')} "
            f"{self.underline('command')} "
            f"{self.underline('help')} "
            "for information on a  specific command.")

        return self.bold("SYNOPSIS") + '\n' + \
            '\n\t'.join([command, description]) + '\n'

    def make_services(self, services):
        available_services = [
                '\to ' + service
                for service in services
            ]
        return self.bold("AVAILABLE SERVICES") + '\n' + \
            '\n\n'.join(available_services)

    def format_page(self):
        page = []
        page.append(self.make_header(self._name))
        page.append(self.make_description(self._description))
        page.append(self.make_synopsis())
        page.append(self.make_services(self._services))
        page.append(self.make_footer(self._name))
        return '\n'.join(page)


class ALCliServiceHelpFormatter(ALCliHelpFormatter):
    def __init__(self,
                 service,
                 width=80,
                 indent_increment=2
                 ):
        super().__init__(width, indent_increment)
        self._service = service
        self._name = service.name
        self._description = service.description
        self._operations = sorted(service.operations)

    def _make_operations(self, operations):
        ops = [
                '\to ' + operation_id
                for operation_id in operations.keys()
            ]
        return self.bold("AVAIABLE COMMANDS") + '\n' + '\n\n'.join(ops)

    def format_page(self):
        page = []
        page.append(self.make_header(self._name))
        page.append(self.make_description(self._description))
        page.append(self._make_operations(self._operations))
        page.append(self.make_footer(self._name))

        return '\n'.join(page)


class ALCliOperationHelpFormatter(ALCliHelpFormatter):
    def __init__(self,
                 operation,
                 width=80,
                 indent_increment=2):
        super().__init__(width, indent_increment)
        self._schema = operation.get_schema()
        self._name = self._schema[OpenAPIKeyWord.OPERATION_ID]
        self._description = self._schema[OpenAPIKeyWord.DESCRIPTION]
        self._params = self._schema[OpenAPIKeyWord.PARAMETERS]

    def make_synopsis(self):
        required = ['\t  ' + self._name]
        optional = []
        for name, value in self._schema[OpenAPIKeyWord.PARAMETERS].items():
            synopsis_value = f"--{name} <value>"
            if not value.get('required'):
                synopsis_value = f"[{synopsis_value}]"
                optional.append('\t' + synopsis_value)
            else:
                required.append('\t' + synopsis_value)
        return self.bold("SYNOPSIS") + '\n' + \
            '\n'.join(required + optional) + '\n'

    def make_options(self):
        param_specs = []

        for name, value in self._schema[OpenAPIKeyWord.PARAMETERS].items():
            type = value.get(OpenAPIKeyWord.TYPE)

            if type == OpenAPIKeyWord.OBJECT:
                type = 'list'
            elif type not in OpenAPIKeyWord.SIMPLE_DATA_TYPES:
                type, alternate_schemas = next(iter(value.items()))

            param_specs.append(
                    self.bold(f"\n\t--{name} ") + f"({type})")

            param_specs.append(
                    '\n'.join(self.wraptext(
                                value.get(OpenAPIKeyWord.DESCRIPTION)
                            )
                        )
                )

            if value.get(OpenAPIKeyWord.ENUM):
                param_specs.append(
                    "\n\t  " +
                    self.bold(f"{name}") +
                    " can be only one of the following values:\n" +
                    '\n'.join(
                        [f"\t   o {v}" for v in value[OpenAPIKeyWord.ENUM]]
                    ) + "\n"
                )

            if type == 'list':
                # Print the structure definition
                for property_name, property_spec in value.get(
                            OpenAPIKeyWord.PROPERTIES, {}).items():
                    param_specs.append(
                        "\n\t   o " + self.bold(f" {property_name}"))

        return self.bold("OPTIONS") + '\n' + '\n'.join(param_specs) + '\n'

    def format_page(self):
        page = []
        page.append(self.make_header(self._name))
        page.append(
                self.make_description(
                    self._description + '\n\n' +
                    FormatHelp.OPERATION_DESCIPTION_FOOTER)
                )
        page.append(self.make_synopsis())
        page.append(self.make_options())
        page.append(self.make_footer(self._name))

        return '\n'.join(page)
