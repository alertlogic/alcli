#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from json import JSONDecodeError
import logging
import argparse
import pydoc

from collections import OrderedDict
from pydoc import pager


import almdrlib
from almdrlib.session import Session
from almdrlib import __version__ as almdrlib_version
from almdrlib.client import OpenAPIKeyWord

from alcli.cliparser import ALCliArgsParser
from alcli.cliparser import USAGE
from alcli.clihelp import ALCliServiceHelpFormatter
from alcli.clihelp import ALCliOperationHelpFormatter

sys.path.insert(0, os.path.dirname(__file__))

logger = logging.getLogger('alcli.almdr_cli')
LOG_FORMAT = (
    '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

#almdrlib.set_logger('almdrlib.session', logging.DEBUG, format_string=LOG_FORMAT)

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
        
        if parsed_args.service == 'help' or parsed_args.service is None:
            sys.stderr.write(f"usage: {USAGE}\n")
            return 128

        if parsed_args.operation == 'help':
            help_page = ALCliServiceHelpFormatter(self._services[parsed_args.service])
            pydoc.pipepager(help_page.format_page() + '\n', 'less -R')
            return 0

        if hasattr(parsed_args, 'help') and \
                hasattr(parsed_args, 'service') and \
                hasattr(parsed_args, 'operation') and \
                parsed_args.help == 'help':
            operation = self._services[parsed_args.service].operations.get(parsed_args.operation)
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
                service_name: ServiceOperation(name=service_name, session=self._session)
                for service_name in services_list
            }

        return self._services

    def _create_parser(self, services):
        parser = ALCliArgsParser(
                services,
                almdrlib_version,
                "Alert Logic CLI Utility",
                prog="alcli")
        
        return parser

class ServiceOperation(object):
    """
        A service operation. For example: alcli aetuner would create
        a ServiceOperation object for aetuner service
    """
    def __init__(self, name, session):
        self._name = name
        self._session = session
        self._service = None
        self._description = None
        self._operations = None

    def __call__(self, args, parsed_globals):
        operation_name = ""
        kwargs = {}
        for name, value in parsed_globals.__dict__.items():
            if name == 'operation':
                operation_name = value
            elif name == 'service':
                continue
            else:
                kwargs[name] = value
        
        # service = self._session.client(self._name)
        operation = self.operations.get(operation_name, None)
        if operation:
            # Remove optional arguments that haven't been supplied
            op_args = {k:self._encode(operation, k, v) for (k,v) in kwargs.items() if v is not None}
            res = operation(**op_args)
            self._print_result(res.json())

    @property
    def service(self):
        if self._service is None:
            self._service = self._session.client(self._name)
        return self._service

    @property
    def name(self):
        return self._name

    @property
    def session(self):
        return self._session

    @property
    def description(self):
        if self._description is None:
            self._description = self.service.description
        return self._description

    @property
    def operations(self):
        if self._operations is None:
            self._operations= self.service.operations
        return self._operations

    def _encode(self, operation, param_name, param_value):
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
                result = dict(
                        (k.strip(), v.strip())
                        for k, v in (kv.split('=')
                        for kv in param_value.split(','))
                    )
                return result
        
        # TODO Raise an exception if we can't build a dictionary from the provided input
        return param_value

    def _print_result(self, result):
        print(f"{json.dumps(result, sort_keys=True, indent=4)}")
        return


def main():
    if os.environ.get("DEBUG"):
        print("Running in DEBUG mode")
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    session = Session()
    cli= AlertLogicCLI(session=session)
    cli.main()

if __name__ == "__main__":
    main()

