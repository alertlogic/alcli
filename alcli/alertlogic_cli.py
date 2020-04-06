#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import platform
import json
import jmespath
from json import JSONDecodeError
import logging
import pydoc

from urllib.parse import urlparse
from collections import OrderedDict

import almdrlib
from almdrlib.session import Session
from almdrlib.client import Client
from almdrlib.client import OpenAPIKeyWord
from almdrlib.region import Region
from almdrlib.region import Residency
from almdrlib import __version__ as almdrlib_version

from alcli.cliparser import ALCliArgsParser
from alcli.clihelp import ALCliMainHelpFormatter
from alcli.clihelp import ALCliServiceHelpFormatter
from alcli.clihelp import ALCliOperationHelpFormatter
from alcli import __version__ as alcli_version

sys.path.insert(0, os.path.dirname(__file__))

logger = logging.getLogger('alcli.almdr_cli')
LOG_FORMAT = (
    '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

GLOBAL_ARGUMENTS = [
        'access_key_id',
        'secret_key',
        'profile',
        'residency',
        'endpoint',
        'query',
        'debug'
    ]


class AlertLogicCLI(object):
    def __init__(self, session=None):
        self._session = session or Session()
        self._subparsers = None
        self._services = None
        self._arguments = None

    def main(self, args=None):
        args = args or sys.argv[1:]
        services = self._get_services()
        parser = self._create_parser(services)

        parsed_args, remaining = parser.parse_known_args(args)
        logger.debug(
                f"Parsed Arguments: {parsed_args}, Remaining: {remaining}")

        if parsed_args.service == 'help' or parsed_args.service is None:
            help_formatter = ALCliMainHelpFormatter(services.keys())
            self._show_help(help_formatter)
            return 128

        if parsed_args.operation == 'help':
            help_formatter = ALCliServiceHelpFormatter(
                        self._services[parsed_args.service])
            self._show_help(help_formatter)
            return 128

        if hasattr(parsed_args, 'help') and \
                hasattr(parsed_args, 'service') and \
                hasattr(parsed_args, 'operation') and \
                parsed_args.help == 'help':
            operation = self._services[parsed_args.service].operations.get(
                                                        parsed_args.operation)
            help_page = ALCliOperationHelpFormatter(operation)
            pydoc.pipepager(help_page.format_page() + '\n', 'less -R')
            return 0

        try:
            return services[parsed_args.service](remaining, parsed_args)
        except Exception as e:
            sys.stderr.write(f"Caught exception in main(). Error: {str(e)}\n")
            return 255

    def _get_services(self):
        if self._services is None:
            self._services = OrderedDict()
            services_list = Session.list_services()
            self._services = {
                service_name: ServiceOperation(name=service_name,
                                               session=self._session)
                for service_name in services_list
            }

        return self._services

    def _create_parser(self, services):
        version = "alcli/{} Python/{} almdrlib/{}".format(
                alcli_version, platform.python_version(), almdrlib_version)

        parser = ALCliArgsParser(
                services,
                version,
                "Alert Logic CLI Utility",
                prog="alcli")

        # Add Global Options
        parser.add_argument('--access_key_id',
                            dest='access_key_id', default=None)
        parser.add_argument('--secret_key',
                            dest='secret_key', default=None)
        parser.add_argument('--profile',
                            dest='profile',  default=None)
        parser.add_argument('--residency',
                            dest='residency', default=None,
                            choices=Residency.list_residencies())
        parser.add_argument('--endpoint',
                            dest='global_endpoint', default=None,
                            choices=Region.list_endpoints())
        parser.add_argument('--query',
                            dest='query', default=None)
        parser.add_argument('--debug',
                            dest='debug', default=False, action="store_true")
        return parser

    def _show_help(self, help_formatter):
        pydoc.pipepager(help_formatter.format_page() + '\n', 'less -R')
        return 0


class ServiceOperation(object):
    """
        A service operation. For example: alcli aetuner would create
        a ServiceOperation object for aetuner service
    """
    def __init__(self, name, session):
        self._name = name
        self._session = session
        self._client = None
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
                    almdrlib.set_logger(
                        'almdrlib', logging.DEBUG, format_string=LOG_FORMAT)
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
            op_args = {
                        k: self._encode(operation, k, v)
                        for (k, v) in kwargs.items() if v is not None
                    }

            res = operation(**op_args)
            self._print_result(res.json(), parsed_globals.query)

    @property
    def client(self):
        if self._client is None:
            self._client = Client(self._name)
        return self._client

    @property
    def name(self):
        return self._name

    @property
    def session(self):
        return self._session

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
        s = Session(
                access_key_id=parsed_globals.access_key_id,
                secret_key=parsed_globals.secret_key,
                profile=parsed_globals.profile,
                global_endpoint=parsed_globals.global_endpoint,
                residency=parsed_globals.residency
                )
        return s.client(self._name)

    def _encode(self, operation, param_name, param_value):
        p = urlparse(param_value)
        if p.scheme == "file":
            value_file_path = os.path.abspath(os.path.join(p.netloc, p.path))
            with open(value_file_path, "r") as value_file:
                param_value = value_file.read()

        schema = operation.get_schema()
        parameter = schema[OpenAPIKeyWord.PARAMETERS][param_name]

        type = parameter[OpenAPIKeyWord.TYPE]
        if type in OpenAPIKeyWord.SIMPLE_DATA_TYPES:
            return param_value

        if type == OpenAPIKeyWord.OBJECT:
            try:
                return json.loads(param_value)
            except JSONDecodeError:
                #
                # this could be an argument encoded using a short form such as
                # key1=value,key2=value2
                #
                result = dict(
                        (k.strip(), v.strip())
                        for k, v in (kv.split('=')
                                     for kv in param_value.split(','))
                    )
                return result

        # TODO: Raise an exception if we can't build a dictionary
        # from the provided input
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

    session = Session()
    cli = AlertLogicCLI(session=session)
    cli.main()


if __name__ == "__main__":
    main()
