import os
import argparse
import platform
import re
import subprocess
import yaml
import sys
import json

app_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
"""The path to the base application directory"""

name = 'rf_classifier'
"""Short name of application associated with executable file"""

version = "0.2"
"""Application version string"""


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
        'models_dir': os.path.join(app_dir, 'models'),
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
                 + "  Fault Labels:  {}" + os.linesep + "  Training Data: {}" + os.linesep + "  Brief:         {}"
    print(fmt_string.format(model_id, desc['releaseDate'], desc['cavityLabels'], desc['faultLabels'],
                            desc['trainingData'], desc['brief']))


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
                 + "  Fault Labels:  {}" + os.linesep + "  Training Data: {}" + os.linesep + "  Brief:         {}"\
                 + os.linesep + "  Details:{}"
    print(fmt_string.format(model_id, desc['releaseDate'], desc['cavityLabels'], desc['faultLabels'],
                            desc['trainingData'], desc['brief'], desc['details']))


def run_model(model_name, config, args=[]):
    """Runs the specified model with the supplied arguments.  Model location dictated by config['models_dir'].

    Note: This will print error messages returned by the model.

    Args:
        model_name (str): The name of the model to run.  Same as model's ID or directory name on the filesystem
        config (dict): The application's configuration dictionary
        args (list:str): The arguments to be passed to the model.  Should be valid paths to event directories.
    Returns:
        dict|None:  Returns dictionary of results representing the JSON out of the model or None if there was a
            problem during execution.
    """

    if platform.system() == "Linux":
        call = [os.path.join(config['models_dir'], model_name, 'bin', 'model.bash')]
    elif platform.system() == "Windows":
        call = ['powershell', os.path.join(config['models_dir'], model_name, 'bin', 'model.ps1')]

    # Model script should return JSON output needed for description
    call.extend(args)
    response = subprocess.run(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if response.stderr != b'':
        print(response.stderr)
    if response.returncode != 0:
        print("{} exited with exit code '{}'".format(model_name, response.returncode))
        return None
    else:
        return json.loads(response.stdout)


def print_model_description(model_name, config, verbose, is_default):
    """Function for reading and print a model's description based on it's description.yaml file.

    Args:
        model_name (str): The name of the model.  Equivalent to it's ID and directory name on the filesystem
        config (dict): The config object for this application
        verbose (bool): Whether to print out the detailed information of the model
        is_default (bool): Is this the default model for the application

    Returns:
        None:  Prints out description or relevant error messages.
    """

    desc_file = os.path.join(config['models_dir'], model_name, "description.yaml")
    if os.path.exists(desc_file):
        with open(desc_file, "r") as f:
            desc = yaml.safe_load(f.read())
            if desc is None:
                print("{} - error getting description".format(f))
            else:
                if verbose:
                    print_detailed_description(desc, is_default)
                else:
                    print_brief_description(desc, is_default)
    else:
        print("{} - description.yaml not found".format(model_name))


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

    # If the query was for a specific model, print more info by default
    if model is not None:
        if os.path.exists(os.path.join(config['models_dir'], model)):
            print_model_description(model_name=model, config=config, verbose=verbose,
                                    is_default=(model == default_model))
        else:
            print("Error: model '{}' not found.".format(model))

    # If the query was for all of the models, only print the names by default
    else:
        dot_pattern = re.compile("\..*")
        for filename in os.listdir(config['models_dir']):
            if os.path.isdir(os.path.join(config['models_dir'], filename)):
                if not dot_pattern.match(filename):
                    if verbose:
                        # Verbose is false here since a detailed listing of all models could take up too much space
                        print_model_description(model_name=filename, config=config, verbose=False,
                                                is_default=(filename == default_model))
                    else:
                        print(filename)


def print_results_table(results, config, header=True):
    """Prints the analysis results in a human readable table.

    Args:
        results (dict): The dictionary contain the results of an analysis.  Should 'data' value from the pluggable model
            API.
        config (dict): The configuration dictionary specifying which model was used in the analysis.
        header (bool): Should a header line be printed.  (Default true).

    Returns:
        None: The results are printed to standard out.
    """

    # Cavity Fault Zone Timestamp Model Cav-Conf Fault-Conf
    fmt = "{:10s} {:19s} {:8s} {:22s} {:20s} {:8s} {:8s}"
    if header:
        print(fmt.format("Cavity", "Fault", "Zone", "Timestamp", "Model", "Cav-Conf", "Fault-Conf"))

    for result in results:
        print(fmt.format(
            result['cavity-label'],
            result['fault-label'],
            result['location'],
            result['timestamp'],
            config['model'],
            str(round(result['cavity-confidence'], 2)) if result['cavity-confidence'] is not None else "N/A",
            str(round(result['fault-confidence'], 2)) if result['fault-confidence'] is not None else "N/A",
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
    analyze_parser.add_argument("-n", "--no-header", help="Do not include a header in the output (only for -o=table)",
                                default=False, dest='no_header', action='store_true')
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

    # We're going to analyze some events
    if args.subparser_name == "analyze":

        # Setup the model in the config object
        if args.model is not None:
            cfg['model'] = args.model
        if cfg['model'] is None:
            print("Error: No default model supplied in config file or on command line.")
            exit(1)
        elif not os.path.exists(os.path.join(cfg['models_dir'], cfg['model'])):
            print("Error: model '{}' not found.".format(cfg["model"]))
            exit(1)

        # Call the appropriate model and get the results
        results = run_model(cfg['model'], cfg, args.events)
        # None implies that the model had some sort of a problem
        if results is None:
            exit(1)
        else:
            if args.output == "json":
                # The model does not include it's name on the response.  Add it to each result.
                for i in range(0, len(results['data'])):
                    results['data'][i]['model'] = cfg['model']
                # A dictionary prints out _VERY_ similarly to JSON, but maybe not exactly.  Just use the json.dump.
                print(json.dumps(results))
            else:
                # If the user doesn't request a support format print out a table
                print_results_table(results['data'], cfg, header=(not args.no_header))
        exit(0)
