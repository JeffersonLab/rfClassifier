import os
import importlib
import pkgutil
import argparse
import re

import yaml
import sys

name = os.path.basename(__file__)
"""Short name of application associated with executable file"""

app_dir = os.path.dirname(os.path.abspath(__file__))
"""The path to the base application directory"""

version = "v0.1"
"""Application version string"""


def parse_config_file(filename=os.path.join(os.path.dirname(__file__), 'config.yaml')):
    """Parses a JSON formatted config file and while supplying some defaults

    Args:
        filename (str):  Path to the config file.

    Returns:
        dict: A dictionary object based on the application defaults and specified configuration file.

    Raises:
        FileNotFoundError: If specified config file is not found or is not a file.
    """

    # Default values for the config file
    default = {
        'ext_config_dir': r'\cs\certified\config\rfClassifier\v1',
        'default_model': None
    }

    if not os.path.isfile(filename):
        raise FileNotFoundError("Cannot find specified config file '" + filename + "'")

    # Read the config file
    with open(filename, "r") as f:
        config = yaml.safe_load(f.read())

    for key in default.keys():
        if key not in config:
            config[key] = default[key]

    config['model'] = config['default_model']

    return config


def list_models(config, model=None, verbose=False):
    """List information about models available to this application

    This function provides a list of available models with optional details.  Should a single model be specified,
    then more detailed information will be provided.

    Args:
        model (str): The model for which information should be listed.  If None, then abbreviated information will
            be generated for all available models.
        verbose (bool): Should more detailed information be provided
        config (dict): A dictionary containing application configuration information

    Returns:
        None: The model information listing is printed to standard out
    """

    default_model = config['default_model']
    sys.path.insert(0, os.path.join(config['ext_config']))
    models = importlib.import_module("models", config['ext_config'])
    if model is not None and model != 'base_model':
        mod = importlib.import_module(".%s.%s" % (model, "model"), models)
        tmp_mod = mod.Model()
        desc = tmp_mod.describe()
        model_id = desc['id']
        if model_id == default_model:
            model_id += " (default)"
        fmt_string = "{}" + os.linesep + "  Release Date:  {}" + os.linesep + "  Cavity Labels: {}" + os.linesep \
                     + "  Fault Labels:  {}" + os.linesep + "  Brief:         {}" + os.linesep + "  Details:{}"
        print(
            fmt_string.format(model_id, desc['releaseDate'], desc['cavLabels'], desc['faultLabels'], desc['brief'],
                              desc['details']))
    else:
        base_pattern = re.compile('^base_model')
        for importer, modname, ispkg in pkgutil.iter_modules(models.__path__):
            if ispkg:
                if base_pattern.match(modname):
                    # Don't list out any of the base_models since a user can't call them directly
                    continue
                if not verbose:
                    if modname == default_model:
                        model_id = modname + " (default)"
                    else:
                        model_id = modname
                    print("%s" % model_id)
                else:
                    try:
                        mod = importlib.import_module(".%s.%s" % (modname, "model"), 'models')
                        desc = mod.Model.describe()
                        model_id = desc['id']
                        if model_id == default_model:
                            model_id += " (default)"

                        fmt_string = "{}" + os.linesep + "  Release Date:  {}" + os.linesep + "  Cavity Labels: {}" + os.linesep \
                                     + "  Fault Labels:  {}" + os.linesep + "  Brief:         {}"
                        print(fmt_string.format(model_id, desc['releaseDate'], desc['cavLabels'], desc['faultLabels'],
                                                desc['brief']))
                        print()
                    except Exception as ex:
                        print("{}: Error accessing info - {}: {}".format(modname, ex.__class__.__name__, ex))


def analyze_event(event_dir, config):
    sys.path.insert(0, os.path.join(config['ext_config']))
    mod = importlib.import_module("models.%s.model" % (config['model']))
    sys.path.pop()
    model = mod.Model(event_dir)
    model.analyze()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="{} {}\nA program that determines the fault type and offending cavity based on a waveform data from a "
                    "C100 fault event".format(name, version),
        epilog="Users may select a specific model if desired.")
    subparsers = parser.add_subparsers(help='commands', dest="subparser_name")

    # Subcommand to list out models
    list_parser = subparsers.add_parser('list_models', help='List out available models')
    list_parser.add_argument('-v', '--verbose', help='Print out detailed model information', action='store_true',
                             default=False)
    list_parser.add_argument('-f', '--config-file', help='Specify an alternate config file', action='store_true',
                             default=app_dir)
    list_parser.add_argument('model', nargs="?", help='A single model to show in more detail', default=None)

    # Subcommand to analyze an event
    analyze_parser = subparsers.add_parser('analyze', help="Analyze a fault event")
    analyze_parser.add_argument("-m", "--model", help="Specify the model to be used", action="store_true",
                                default=False)
    analyze_parser.add_argument("event", nargs=1, help="The path to the fault event directory", default=None)

    args = parser.parse_args()
    if args.subparser_name is None:
        print("%s %s" % (name, version))
        sys.exit(0)

    config = parse_config_file(os.path.join(app_dir, 'config.yaml'))

    if args.subparser_name == "list_models":
        list_models(config, args.model, args.verbose)

    if args.subparser_name == "analyze":
        for event in args.event:
            print(os.path.islink(event))
            analyze_event(event, config)
