import os
import importlib
import pkgutil
import argparse
import re

import yaml
import sys
import json

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


def print_brief_description(desc, is_default=False):
    """Prints out a model description in a brief format.

        Args:
            desc (dict): A dictionary containing the description of a model.
            is_default (bool): Is this model currently the default model for the application

        Returns:
            None: The model description is printed to standard out.
    """
    model_id = desc['id']
    if is_default:
        model_id += " (default)"

    fmt_string = "{}" + os.linesep + "  Release Date:  {}" + os.linesep + "  Cavity Labels: {}" + os.linesep \
                 + "  Fault Labels:  {}" + os.linesep + "  Brief:         {}"
    print(fmt_string.format(model_id, desc['releaseDate'], desc['cavLabels'], desc['faultLabels'], desc['brief']))


def print_detailed_description(desc, is_default=False):
    """Prints out a model description in a detailed format.

        Args:
            desc (dict): A dictionary containing the description of a model.
            is_default (bool): Is this model currently the default model for the application

        Returns:
            None: The model description is printed to standard out.
    """
    model_id = desc['id']
    if is_default:
        model_id += " (default)"

    fmt_string = "{}" + os.linesep + "  Release Date:  {}" + os.linesep + "  Cavity Labels: {}" + os.linesep \
                 + "  Fault Labels:  {}" + os.linesep + "  Brief:         {}" + os.linesep + "  Details:{}"
    print(fmt_string.format(model_id, desc['releaseDate'], desc['cavLabels'], desc['faultLabels'], desc['brief'],
                            desc['details']))


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
    base_pattern = re.compile('^base_model')

    # If the query was for a specific model, print more info by default
    if model is not None and model != 'base_model':
        try:
            mod = importlib.import_module("models.%s.model" % model)
        except Exception as ex:
            print("Error importing model - {}: {}".format(ex.__class__.__name__, ex))
            return

        desc = mod.Model.describe()
        if verbose:
            print_detailed_description(desc, desc['id'] == default_model)
        else:
            print_brief_description(desc, desc['id'] == default_model)

    # If the query was for all of the models, only print the names by default
    else:
        for importer, modname, is_package in pkgutil.iter_modules(models.__path__):
            if is_package:
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
                        print_brief_description(desc, modname == default_model)
                        print()
                    except Exception as ex:
                        print("{}: Error accessing info - {}: {}".format(modname, ex.__class__.__name__, ex))


def analyze_event(event_dir, config):
    """Loads the model specified by config['model'] and uses it to analyze the given event_dir.

    Args:
        event_dir (str): The path to the fault event directory to be analyzed config.
        config (dict): The configuration dictionary specifying the external config directory and which model to load.

    Returns:
         dict:  A dictionary containing the results of the analysis.  Should meet the pluggable model API.
    """
    sys.path.insert(0, os.path.join(config['ext_config']))
    try:
        mod = importlib.import_module("models.%s.model" % (config['model']))
    except Exception as ex:
        print("Error loading model: {}".format(ex))
        exit(1)
    sys.path.pop()
    model = mod.Model(event_dir)
    return model.analyze()


def print_results_table(results, config, header=True):
    """Prints the analysis results in a human readable table.

    Args:
        results (dict): The dictionary contain the results of an analysis.  Should meet the pluggable model API.
        config (dict): The configuration dictionary specifying which model was used in the analysis.
        header (bool): Should a header line be printed.  (Default true).

    Returns:
        None: The results are printed to standard out.
    """

    # Cavity Fault Zone Timestamp Model Cav-Conf Fault-Conf
    fmt = "{:17s} {:17s} {:12s} {:22s} {:20s} {:10s} {:10s}"
    if header:
        print(fmt.format("Cavity", "Fault", "Zone", "Timestamp", "Model", "Cav-Conf", "Fault-Conf"))

    print(fmt.format(
        results['cavity-label'],
        results['fault-label'],
        results['location'],
        results['timestamp'],
        config['model'],
        str(round(results['cavity-confidence'], 2)) if results['cavity-confidence'] is not None else "N/A",
        str(round(results['fault-confidence'], 2)) if results['fault-confidence'] is not None else "N/A",
    ))


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
    analyze_parser.add_argument("-m", "--model", help="Specify the model to be used",
                                default=None, dest='model')
    analyze_parser.add_argument("-o", "--output", help="Specify the output format (default: table)",
                                default="table", dest='output')
    analyze_parser.add_argument("-c", "--config", help="Specify the config file (default: config.yaml)",
                                default=None, dest='config_file')
    analyze_parser.add_argument("events", nargs='+', help="The path to the fault event directory", default=None)

    args = parser.parse_args()
    if args.subparser_name is None:
        print("%s %s" % (name, version))
        sys.exit(0)

    config_file = 'config.yaml' if args.config_file is None else args.config_file
    try:
        cfg = parse_config_file(os.path.join(app_dir, config_file))
    except FileNotFoundError as ex:
        print("Error parsing config file: " + str(ex))
        exit(1)

    if args.subparser_name == "list_models":
        list_models(cfg, args.model, args.verbose)

    if args.subparser_name == "analyze":
        if args.model is not None:
            cfg['model'] = args.model
        if cfg['model'] is None:
            print("Error: No default model supplied in config file or on command line.")
            exit(1)

        exit_val = 0
        out = []
        for event in args.events:
            try:
                result = analyze_event(event, cfg)
                out.append(result)
            except Exception as ex:
                exit_val += 1
                print("Error analyzing " + event)
                print("  " + ex.__class__.__name__ + ": " + str(ex))

        if args.output == "json":
            print(json.dumps(out, indent=2))
        else:
            header = True
            for result in out:
                print_results_table(result, cfg, header=header)
                header = False

        exit(exit_val)