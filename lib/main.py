import os
import importlib
import pkgutil
import argparse
import re

import yaml
import sys
import json

app_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
"""The path to the base application directory"""

name = 'rf_classifier'
"""Short name of application associated with executable file"""

version = "0.1"
"""Application version string"""


def insert_model_syspath(model_name, model_dir=os.path.join(app_dir, 'models')):
    """Convenience function for including a model's virtualenv library in the application sys.path

    Note: Use pop_model_syspath() to undo.  Do not make any additional changes to the path before calling
          pop_model_syspath() as it's implementation may be very naive.
    Args:
        model_name (str): The name of the model.  Should match the name on the model package directory
        model_dir (str): The directory path to the models directory. Should be the parent of the model package directory

    Returns:
        None
    """
    sys.path.insert(0, os.path.join(model_dir, model_name, 'venv', 'lib', 'site-packages'))
    sys.path.insert(0, os.path.join(model_dir, model_name))

def pop_model_syspath():
    """Convenience function for removing a model's directories from sys.path that were added via insert_model_syspath

    Returns:
        None
    """

    # The current insert_model_syspath merely adds two directories to the front of sys.path.  pop(0) removes the first
    # element.  This simple approach is sufficient for our use case where we add a path, run some model code, then
    # remove it immediately.  Any thing more complex than that would require that the path be searched, etc. but trying
    # to match paths based on model names risks removing the wrong entries and is not needed.
    sys.path.pop(0)
    sys.path.pop(0)

def parse_config_file(filename=os.path.join(app_dir, 'cfg', 'config.yaml')):
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
        'models_dir': os.path.join('cs','certified', 'apps', name, version, 'models'),
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
    sys.path.insert(0, os.path.join(config['model_dir']))
    models = importlib.import_module("models", config['model_dir'])
    base_pattern = re.compile('^base_model')

    # If the query was for a specific model, print more info by default
    if model is not None and model != 'base_model':
        try:
            insert_model_syspath(model)
            mod = importlib.import_module("models.%s.model" % model)
            pop_model_syspath()
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
                        insert_model_syspath(modname)
                        mod = importlib.import_module(".%s.%s" % (modname, "model"), 'models')
                        pop_model_syspath()
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
    sys.path.insert(0, os.path.join(config['model_dir']))
    try:
        mod = importlib.import_module("models.%s.model" % (config['model']))
    except Exception as ex:
        print("Error loading model: {}".format(ex))
        exit(1)
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
        description="{} v{}\nA program that determines the fault type and offending cavity based on a waveform data from a "
                    "C100 fault event".format(name, version),
        epilog="Users may select a specific model if desired.")
    parser.add_argument("-c", "--config", help="Specify config file (default: " + os.path.join('cfg', 'config.yaml') + ")",
                        default=os.path.join(app_dir, 'cfg', 'config.yaml'), dest='config_file')
    parser.add_argument("-M", "--models_dir", help="Specify the directory contain the models package", default=None,
                        dest='models_dir')
    subparsers = parser.add_subparsers(help='commands', dest="subparser_name")

    # Subcommand to list out models
    list_parser = subparsers.add_parser('list_models', help='List out available models')
    list_parser.add_argument('-v', '--verbose', help='Print out detailed model information', action='store_true',
                             default=False)
    list_parser.add_argument('model', nargs="?", help='A single model to show in more detail', default=None)

    # Subcommand to analyze an event
    analyze_parser = subparsers.add_parser('analyze', help="Analyze a fault event")
    analyze_parser.add_argument("-m", "--model", help="Specify the model to be used",
                                default=None, dest='model')
    analyze_parser.add_argument("-o", "--output", help="Specify the output format (default: table)",
                                default="table", dest='output')
    analyze_parser.add_argument("events", nargs='+', help="The path to the fault event directory", default=None)

    # Parse command line arguments.  Print out the certified name/version if none is specified
    args = parser.parse_args()
    if args.subparser_name is None:
        print("%s v%s" % (name, version))
        sys.exit(0)

    config_file = args.config_file
    try:
        cfg = parse_config_file(config_file)
    except FileNotFoundError as ex:
        print("Error parsing config file: " + str(ex))
        exit(1)

    # Override the models_dir cfg parameter if one is specified
    if args.models_dir is not None:
        cfg['models_dir'] = args.models_dir

    if args.subparser_name == "list_models":
        list_models(cfg, args.model, args.verbose)

    if args.subparser_name == "analyze":
        if args.model is not None:
            cfg['model'] = args.model
        if cfg['model'] is None:
            print("Error: No default model supplied in config file or on command line.")
            exit(1)

        # Load the add the venv package directoy of the specificed model into sys.path
        insert_model_syspath(cfg['model'])
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
        # Remove the model's venv, etc. from sys.path
        pop_model_syspath()

        exit(exit_val)
