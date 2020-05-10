#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import textwrap
import itertools
from almdrlib.session import Session
from almdrlib.region import Region
from almdrlib.region import Residency
from almdrlib.docs.service import get_param_spec
from almdrlib.docs.service import format_json

def get_param_type(spec):
    type = spec.get('type')
    format = spec.get('format')

    if type == 'object':
        return 'list'
    elif type == 'array':
        return 'list'
    elif format:
        return format
    elif type:
        return type
    else:
        if 'oneOf' in spec:
            one_of_spec = spec['oneOf']
            return ' | '.join(list(set([
                    get_param_type(s)
                    for s in one_of_spec
                ])))
        elif 'anyOf' in spec:
            any_of_spec = spec['anyOf']
            return ' | '.join(list(set([
                    get_param_type(s)
                    for s in one_of_spec
                ])))
        else:
            raise ValueError(
                f'Unsupported parameter type. {json.dumps(spec, indent=2)}')

class FormatHelp:
    if sys.platform == 'win32':
        BOLD = ''
        UNDERLINE = ''
        END = ''
    elif hasattr(os, 'system') and os.system('(less) 2>/dev/null') == 0:
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'
    else:
        BOLD = ''
        UNDERLINE = ''
        END = ''

    SECTION_BREAK = '\n'*2
    OPERATION_DESCIPTION_FOOTER = "See 'alcli help' for descriptions of global parameters."


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

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description


    def bold(self, msg):
        return f"{FormatHelp.BOLD}{msg}{FormatHelp.END}"

    def underline(self, msg):
        return f"{FormatHelp.UNDERLINE}{msg}{FormatHelp.END}"

    def wraptext(self, text, initial_indent=None, subsequent_indent=None):
        if text is None:
            return 

        if not initial_indent:
            initial_indent = self._initial_indent

        if not subsequent_indent:
            subsequent_indent = self._subsequent_indent

        for str in text.splitlines():
            yield textwrap.fill(
                        text=f"{str}",
                        width=self._width - 6, # Not sure why, but this seem to align description correctly
                        initial_indent=initial_indent,
                        subsequent_indent=subsequent_indent
                    )

    def make_header(self):
        title_name = self.name.upper() + "()"
        title = title_name + title_name.rjust(self._width - len(title_name))
        yield f'{title}'
        yield FormatHelp.SECTION_BREAK
        yield f'{self.bold("NAME")}'
        yield f'\t{self.name} - '
        yield ''

        
    def make_footer(self):
        footer_title = self.name.upper() + "()"
        fill_text = " " * (self._width - len(footer_title))
        yield f'{fill_text}{footer_title}'

    def make_description(self):
        if not self.description:
            yield ''
        yield f'{self.bold("DESCRIPTION")}'
        yield from self.wraptext(self.description)
        yield f''

class ALCliMainHelpFormatter(ALCliHelpFormatter):
    def __init__(self,
                services,
                width=80,
                indent_increment=2
                ):
        super().__init__(width, indent_increment)
        self.name = "alcli"
        self._services = services 
        self.description = (
                "The Alert Logic Command  Line  Interface is a tool "
                "to help you manage Alert Logic Services."
            )

    def make_synopsis(self):
        yield f'{self.bold("SYNOPSIS")}'
        yield f'\t  alcli [options] <command> <subcommand> [parameters]'
        synopsis = (
                f"\tUse {self.underline('alcli')} "
                f"{self.underline('command')} "
                f"{self.underline('help')} "
                "for information on a  specific command."
            )
        yield ''
        yield synopsis
        yield ''

    def make_options(self):
        yield f'{self.bold("OPTIONS")}'
        yield f'\t{self.bold("--debug")} (boolean)'
        yield ''
        yield '\tTurn on debug logging.'
        yield ''

        yield f'\t{self.bold("--query")} (string)'
        yield ''
        yield '\tA JMESPath query to use in filtering the response data.'
        yield ''

        yield f'\t{self.bold("--global_endpoint")} (string)'
        yield ''
        yield f'\tUse specific Alert Logic backend.'
        yield ''
        for endpoint in Region.list_endpoints():
            yield f'\to {endpoint}'
            yield ''

        yield f'\t{self.bold("--residency")} (string)'
        yield ''
        yield f'\tUse a specific data residency.'
        yield ''
        for residency in Residency.list_residencies():
            yield f'\to {residency}'
            yield ''

        yield f'\t{self.bold("--profile")} (string)'
        yield ''
        yield f'\tUse a specific profile from your configuration file.'
        yield ''

        yield f'\t{self.bold("--version")} (string)'
        yield ''
        yield '\tDisplay the version of alcli.'
        yield ''

    def make_services(self):
        yield f'{self.bold("AVAIABLE SERVICES")}'
        for service in self._services:
            yield f'\to {service}'
            yield ''

    def get_help(self):
        generators = []
        generators.append(self.make_header())
        generators.append(self.make_description())
        generators.append(self.make_synopsis())
        generators.append(self.make_options())
        generators.append(self.make_services())
        generators.append(self.make_footer())
        return iter(itertools.chain(*generators))


class ALCliServiceHelpFormatter(ALCliHelpFormatter):
    def __init__(self,
                name,
                spec,
                width=80,
                indent_increment=2
                ):
        super().__init__(width, indent_increment)
        self.name = name
        self.description = spec['info'].get('description', '')
        self._spec = spec 

    def make_operations(self):
        yield f'{self.bold("AVAIABLE COMMANDS")}'
        commands = sorted(self._spec.get('operations', {}).keys())
        for name in commands:
            yield f'\t o {name}'
            yield ''

    def get_help(self):
        generators = []
        generators.append(self.make_header())
        generators.append(self.make_description())
        generators.append(self.make_operations())
        generators.append(self.make_footer())
        return iter(itertools.chain(*generators))


class ALCliOperationHelpFormatter(ALCliHelpFormatter):
    def __init__(self,
                spec,
                width=80,
                indent_increment=2
                ):
        super().__init__(width, indent_increment)
        self.name = spec['operationId'] 
        self.description = spec['description']
        self._spec = spec 

        self._required_params = dict()
        self._params = dict()
        for key, value in spec.get('parameters', {}).items():
            if 'required' in value or 'x-alertlogic-required' in value:
                self._required_params[key] = value
            else:
                self._params[key] = value

    def make_description(self):
        if not self.description:
            yield ''
        yield f'{self.bold("DESCRIPTION")}'
        yield from self.wraptext(self.description)
        yield f''
        yield f"\tSee 'alcli help' for descriptions of global parameters."
        yield f''

    def make_synopsis(self):
        yield f'{self.bold("SYNOPSIS")}'
        yield f'\t  {self.name}'
        for name in self._required_params.keys():
            yield f'\t--{name} <value>'

        for name in self._params.keys():
            yield f'\t[--{name} <value>]'
        yield f''

    def make_options(self):
        yield f'{self.bold("OPTIONS")}'
        yield from self.make_parameters(self._required_params)
        yield from self.make_parameters(self._params)

    def make_output(self):
        yield f'{self.bold("OUTPUT")}'

        indent = '\t'
        spec = self._spec.get('response', {})
        if not bool(spec):
            yield f"{indent}This command doesn't produce an output"

        type = spec.get('type')
        if 'object' == type:
            yield f'{indent}{spec.get("title", "")} -> (structure)'
            indent = indent + '  '
            
            yield from self.wraptext(
                    spec.get('description'),
                    initial_indent=indent, subsequent_indent=indent)
            yield ''

            for name, spec in spec.get('properties', {}).items():
                yield f'{indent}{name} -> ({get_param_type(spec)})'
                yield from self.make_parameter(
                        spec, param_type='response', indent=indent + '  ', declare=True)
                yield ''
            return 

        elif 'array' == type:
            indent = indent + '  '
            yield f'{indent}{spec.get("x-alertlogic-name", "")} -> (list)'
        else:
            indent = indent + '  '

        yield from self.make_parameter(
                spec, param_type='response', indent=indent, declare=True)

    def make_parameters(self, params):
        for name, spec in params.items():
            if 'content' in spec:
                type = ' | '.join([
                        get_param_type(v)
                        for v in spec['content'].values()
                    ])
            else:
                type = get_param_type(spec)

            yield self.bold(f'\t--{name} ') + f'({type})'
            yield from self.make_parameter(
                    spec, param_type='request', indent='\t  ', declare=True)
            yield ''
            # print(f'{name}: {json.dumps(spec, indent=2)}')

    def make_parameter(self, spec, param_type='request', indent='\t', declare=False):
        type = spec.get('type')

        if type and declare:
        # if type:
            yield from self.wraptext(
                    spec.get('description'),
                    initial_indent=indent,
                    subsequent_indent=indent
                )
            yield ''

        if type == 'array':
            if 'items' in spec:
                yield from self.make_parameter(
                        spec['items'],
                        param_type=param_type, indent=indent, declare=declare)

        elif type == 'object':
            if declare and param_type == 'request':
                yield ''
                yield f'{indent}JSON Syntax:'
                yield ''
                json_indent=indent + '  '
                json_spec = format_json(
                        get_param_spec(spec),
                        json_indent).replace("'", "").replace("|", " | ")
                yield f'{json_indent}{json_spec}'
                yield ''

            properties = spec.get('properties', {})
            for prop_name, prop_spec in sorted(properties.items()):
                yield ''
                prop_title = (
                        f'o {self.bold(prop_name)} - '
                        f'{prop_spec.get("description", "")}'
                    )

                yield from self.wraptext(
                        prop_title,
                        initial_indent=indent,
                        subsequent_indent=indent + '  '
                    )

                yield from self.make_parameter(
                        spec=prop_spec,
                        param_type=param_type,
                        indent=indent + '  ',
                        declare=False
                    )

        elif 'oneOf' in spec:
            yield from self.make_indirect_parameter(
                'oneOf', spec.get('oneOf', []),
                param_type=param_type, indent=indent, declare=declare)

        elif 'anyOf' in spec:
                yield from self.make_indirect_parameter(
                    'anyOf', spec.get('anyOf', []),
                    param_type=param_type, indent=indent, declare=declare)
        elif 'content' in spec:
            yield from self.make_body_parameter(
                    spec.pop('content'), indent=indent, declare=declare)

        if 'enum' in spec:
            yield ''
            valid_values = ', '.join([f'{v}' for v in spec['enum']]) 
            yield f'{indent} Valid values: {valid_values}'

        if 'default' in spec:
            yield ''
            yield f'{indent} Default: {spec["default"]}'

    def make_indirect_parameter(self, indirect_type, spec, 
            param_type='request', indent='\t', declare=False):
        yield ''
        if indirect_type == 'oneOf':
            yield f'{indent}This argument must be one of the following:'
        else:
            yield f'{indent}This argument must be any of the following:'

        for s in spec:
            yield ''
            title = self.bold(s.get('title')) + \
                    f' ({get_param_type(s)}) - ' + \
                    s.get('description')
            yield from self.wraptext(
                    title,
                    initial_indent=indent,
                    subsequent_indent=indent + '  '
                )

            yield from self.make_parameter(
                    s, param_type, indent + '  ', declare)

    def make_body_parameter(self, spec, indent='\t', declare=False):
        yield f"{indent}This argument depends 'content_type' argument value"
        for content_type, content_spec in sorted(spec.items()):
            yield ''
            yield f'{indent}--content_type={content_type}:'
            yield from self.make_parameter(
                    spec=content_spec, indent=indent + '  ', declare=True)

    def get_help(self):
        generators = []
        generators.append(self.make_header())
        generators.append(self.make_description())
        generators.append(self.make_synopsis())
        generators.append(self.make_options())
        generators.append(self.make_output())
        generators.append(self.make_footer())
        return iter(itertools.chain(*generators))

