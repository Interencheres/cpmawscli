import argparse
import coloredlogs
import inspect
import logging

import CpmAWS.plugins
from CpmAWS.core.Configuration import Configuration
from CpmAWS.core.Parameters import Parameters


class Orchestrator():
    parser = None
    plugins = {}
    parameters = None
    configuration = None

    def __init__(self):
        logging.debug('CpmOrchestrator Init')
        # as the plugin list is dynamically constructed, parser is managed by this class
        self.configuration = Configuration()
        self.parser = argparse.ArgumentParser(description='AWS CPM Toolbox')

        subparsers = self.parser.add_subparsers(help='sub-command help')
        # for each plugin add command
        for pluginname in self.getPluginList():
            logging.debug('Plugin found ' + pluginname)
            subparser = subparsers.add_parser(pluginname, help=pluginname + ' help')
            subparser.set_defaults(type=pluginname)
            actionparser = subparser.add_subparsers(help=pluginname + ' help')
            # for each plugin action add sub command
            for action in self.getPluginActions(pluginname):
                logging.debug('Action found ' + action)
                actionsubparser = actionparser.add_parser(action, help='action ' + action)
                actionsubparser.set_defaults(action=action)

        # filtering by instance and tag is mutually exclusive
        exclusivegroup = self.parser.add_mutually_exclusive_group(required=True)
        exclusivegroup.add_argument('--tag', help='tagkey,tagvalue for filtering', nargs=2, metavar=('key', 'value'),
                                    action='append', required=False)
        exclusivegroup.add_argument('--instance', help='specific instance', required=False)

        self.parser.add_argument('--dryrun', help='dryrun mode', action='store_true', required=False)
        self.parser.add_argument('--exclude',
                                 help='exclude specific instance name',
                                 nargs='*',
                                 required=False)
        self.parser.add_argument('--loglevel',
                                 help='log level (debug,info,notice,warning,error,critical',
                                 choices=['debug', 'info', 'notice', 'warning', 'error', 'critical'],
                                 default='notice',
                                 required=False)
        self.parser.add_argument('--aws_access_key_id', help='The access key to use when creating the client',
                                 required=False)
        self.parser.add_argument('--aws_secret_access_key', help='The secret key to use when creating the client.',
                                 required=False)

        self.parameters = Parameters(self.parser.parse_args())
        coloredlogs.install(level=self.parameters.loglevel.upper(),
                            fmt=self.configuration.get('logformat'),
                            field_styles={'asctime': {'color': 'white'}},
                            level_styles=self.configuration.get('logcolors'))

    def getPluginList(self):
        # @TODO find other way to filter classes
        return [mod for mod in dir(CpmAWS.plugins) if not mod.startswith('__')]

    def getPluginActions(self, name):
        object = getattr(getattr(CpmAWS.plugins, name), name)(self)
        return [attr for attr in dir(object) if inspect.ismethod(getattr(object, attr)) and not attr.startswith('__')]

    def run(self):
        module = getattr(CpmAWS.plugins, self.parameters.type)
        object = getattr(module, self.parameters.type)(self)
        ok = getattr(object, self.parameters.action)()
        if ok:
            logging.debug('run ok')
            exit(0)
        else:
            logging.debug('run failed')
            exit(1)
