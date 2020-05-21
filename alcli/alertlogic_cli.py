#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import platform
import json
import jmespath
from json import JSONDecodeError
import logging
import argparse
import re
import pydoc

from urllib.parse import urlparse
from collections import OrderedDict
from pydoc import pager


import almdrlib
from almdrlib.session import Session
from almdrlib.client import Client
from almdrlib.client import OpenAPIKeyWord
from almdrlib.region import Region
from almdrlib.region import Residency
from almdrlib import __version__ as almdrlib_version

from alcli.cliparser import ALCliArgsParser
from alcli.cliparser import USAGE
from alcli.clihelp import ALCliMainHelpFormatter
from alcli.clihelp import ALCliServiceHelpFormatter
from alcli.clihelp import ALCliOperationHelpFormatter
from alcli import __version__ as alcli_version

if getattr(sys, 'frozen', False):
    # frozen
    dir_ = os.path.dirname(sys.executable)
else:
    # unfrozen
    dir_ = os.path.dirname(os.path.dirname(__file__))

sys.path.insert(0, dir_)
# sys.path.insert(0, os.path.dirname(__file__))

logger = logging.getLogger('alcli.almdr_cli')
LOG_FORMAT = (
    '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

GLOBAL_ARGUMENTS = [
        'access_key_id',
        'secret_key',
        'profile',
        'residency',
        'global_endpoint',
        'query',
        'debug'
    ]

def cli_pager(text):
    """The first time this is called, determine what kind of pager to use."""
    global cli_pager
    cli_pager = get_cli_pager()
    cli_pager(text)

def get_cli_pager():
    if sys.platform == 'win32':
        return lambda text: pydoc.pipepager(text, 'more /C')
    if hasattr(os, 'system') and os.system('(less) 2>/dev/null') == 0:
        return lambda text: pydoc.pipepager(text, 'less -R')

class AlertLogicCLI(object):
    def __init__(self):
        self._subparsers = None
        self._services = None
        self._arguments = None

    def main(self, args=None):
        args = args or sys.argv[1:]
        services = self._get_services()
        parser = self._create_parser(services)

        parsed_args, remaining = parser.parse_known_args(args)
        logger.debug(f"Parsed Arguments: {parsed_args}, Remaining: {remaining}")
        
        if parsed_args.service == 'help' or parsed_args.service is None:
            AlertLogicCLI.show_help(
                     ALCliMainHelpFormatter(Session.list_services())
                )
            return 128

        if parsed_args.operation == 'help':
            AlertLogicCLI.show_help(
                    ALCliServiceHelpFormatter(
                        parsed_args.service,
                        Session.get_service_api(parsed_args.service)
                    )
                )
            return 128

        if hasattr(parsed_args, 'help') and \
                hasattr(parsed_args, 'service') and \
                hasattr(parsed_args, 'operation') and \
                parsed_args.help == 'help':
            spec = Session.get_service_api(parsed_args.service)['operations']
            AlertLogicCLI.show_help(
                    ALCliOperationHelpFormatter(
                        spec.get(parsed_args.operation, {})
                    )
                )
            return 0

        try:
            return services[parsed_args.service](remaining, parsed_args)
        except almdrlib.exceptions.AlmdrlibValueError as e:
            sys.stderr.write(f"{e}\n")
            return 255
        except almdrlib.session.AuthenticationException as e:
            sys.stderr.write("Access Denied\n")
            return 255
        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            logger.exception(message)
            return 255

    def _get_services(self):
        if self._services is None:
            self._services = OrderedDict()
            services_list = Session.list_services()
            self._services = {
                service_name: ServiceOperation(name=service_name)
                for service_name in services_list
            }

        return self._services

    def _create_parser(self, services):
        parser = ALCliArgsParser(
                services,
                f"alcli/{alcli_version} Python/{platform.python_version()} almdrlib/{almdrlib_version}",
                "Alert Logic CLI Utility",
                prog="alcli")
        
        # Add Global Options
        parser.add_argument('--access_key_id', dest='access_key_id', default=None)
        parser.add_argument('--secret_key', dest='secret_key', default=None)
        parser.add_argument('--profile', dest='profile', default=None)
        parser.add_argument('--residency', dest='residency', default=None, choices=Residency.list_residencies())
        parser.add_argument('--global_endpoint', dest='global_endpoint', default=None, choices=Region.list_endpoints())
        parser.add_argument('--query', dest='query', default=None)
        parser.add_argument('--debug', dest='debug', default=False, action="store_true")
        return parser

    @staticmethod
    def show_help(help_generator):
        # cli_pager(help_formatter.format_page() + '\n')
        cli_pager('\n'.join(list(help_generator.get_help())) + '\n')
        return 0


class ServiceOperation(object):
    """
        A service operation. For example: alcli aetuner would create
        a ServiceOperation object for aetuner service
    """
    def __init__(self, name):
        self._name = name
        self._client= None
        #self._service = None
        self._description = None
        self._operations = None

    def __call__(self, args, parsed_globals):
        operation_name = ""
        kwargs = {}
        for name, value in parsed_globals.__dict__.items():
            if name == 'operation':
                operation_name = value
            elif name == 'debug': 
                if value:
                    almdrlib.set_logger('almdrlib', logging.DEBUG, format_string=LOG_FORMAT)
            elif name == 'service':
                continue
            elif name in GLOBAL_ARGUMENTS:
                continue
            else:
                kwargs[name] = value
        
        service = self._init_service(parsed_globals)
        operation = service.operations.get(operation_name, None)
        if operation:
            # Remove optional arguments that haven't been supplied
            op_args = {k:self._encode(operation, k, v) for (k,v) in kwargs.items() if v is not None}
            res = operation(**op_args)
            try:
                self._print_result(res.json(), parsed_globals.query)
            except json.decoder.JSONDecodeError:
                print(f'HTTP Status Code: {res.status_code}')

    def get_service_api(self, service_name):
        return Session.get_service_api(service_name=service_name)

    @property
    def client(self):
        if self._client is None:
            self._client = Client(self._name)
        return self._client

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        if self._description is None:
            self._description = self.client.description
        return self._description

    @property
    def operations(self):
        if self._operations is None:
            self._operations = self.client.operations
        return self._operations

    def _init_service(self, parsed_globals):
        return almdrlib.client(
                self._name,
                access_key_id=parsed_globals.access_key_id,
                secret_key=parsed_globals.secret_key,
                account_id=parsed_globals.account_id,
                profile=parsed_globals.profile,
                global_endpoint=parsed_globals.global_endpoint,
                residency=\
                        parsed_globals.residency and \
                        parsed_globals.residency or "default"
        )

    def _encode(self, operation, param_name, param_value):
        if isinstance(param_value, str):
            p = urlparse(param_value)
            if p.scheme == "file":
                value_file_path = os.path.abspath(os.path.join(p.netloc, p.path))
                with open (value_file_path, "r") as value_file:
                    param_value = value_file.read()

        schema = operation.get_schema()
        parameter = schema[OpenAPIKeyWord.PARAMETERS][param_name]

        type = parameter[OpenAPIKeyWord.TYPE]
        if type in OpenAPIKeyWord.SIMPLE_DATA_TYPES:
            return param_value
        
        if type == OpenAPIKeyWord.OBJECT:
            try:
                return json.loads(param_value)
            except JSONDecodeError as e:
                #
                # this could be an argument encoded using a short form such as
                # key1=value,key2=value2
                #
                regex = re.compile(
                        '(?P<pair>(?P<key>.+?)(?:=)(?P<value>[^=]+)(?:,|$))')
                result = dict(
                    (m.groupdict()['key'], m.groupdict()['value'])
                    for m in regex.finditer(param_value)
                )
                return result

        # TODO Raise an exception if we can't build a dictionary from the provided input
        return param_value

    def _print_result(self, result, query):
        if query:
            result = jmespath.search(query, result) 
        print(f"{json.dumps(result, sort_keys=True, indent=4)}")


def main():
    if os.environ.get("DEBUG"):
        print("Running in DEBUG mode")
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    cli= AlertLogicCLI()
    cli.main()

if __name__ == "__main__":
    main()

