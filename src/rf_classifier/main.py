import os
import argparse
from typing import Dict, Any

import sys
import json

app_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
"""The path to the base application directory"""

name = 'rf_classifier'
"""Short name of application associated with executable file"""

version = "2.0.0"
"""Application version string"""


def run_model(events):
    """Runs the embedded model with the supplied arguments.

    Args:
        events (list:str): The arguments to be passed to the model.  Should be valid paths to event directories.
    Returns:
        dict|None:  Returns dictionary of results representing the JSON out of the model or None if there was a
            problem during execution.
    """

    # This takes a little while to import as it relies on some heavy duty packages (e.g., numpy).  Only load it here
    # so help calls, etc. are very snappy.
    from .model.model import Model

    results = []
    model = Model()
    for i in range(len(events)):
        try:
            model.update_example(events[i])
            results.append(model.analyze())
        except Exception as ex:
            results.append({
                # ex[1] is the exception message
                'error': f"{ex}",
                'location': model.zone_name,
                'timestamp': model.fault_time
            })
    return {'data': results}


def print_results_table(results: Dict[str, Any], header=True):
    """Prints the analysis results in a human readable table.

    Args:
        results (dict): The dictionary contain the results of an analysis.  Should 'data' value from the pluggable model
            API.
        header (bool): Should a header line be printed.  (Default true).

    Returns:
        None: The results are printed to standard out.
    """

    # Cavity Fault Zone Timestamp Model Cav-Conf Fault-Conf
    fmt = "{:10s} {:19s} {:8s} {:22s} {:20s} {:8s} {:8s}"
    first_result = True
    for result in results:
        # A result containing an error key will be shown below
        if "error" not in result.keys():

            # We could have received all errors so don't print a header unless needed
            if first_result:
                first_result = False
                if header:
                    print(fmt.format("Cavity", "Fault", "Zone", "Timestamp", "Model", "Cav-Conf", "Fault-Conf"))

            print(fmt.format(
                result['cavity-label'],
                result['fault-label'],
                result['location'],
                result['timestamp'],
                result['model'],
                str(round(result['cavity-confidence'], 2)) if result['cavity-confidence'] is not None else "N/A",
                str(round(result['fault-confidence'], 2)) if result['fault-confidence'] is not None else "N/A",
            ))

    first_error = True
    err_fmt = "{:8s} {:22s} {}"
    for result in results:
        # Result with an error key will be handled here
        if "error" in result.keys():

            # We might not have received any errors.  Only print the header if needed.
            if first_error:
                print(err_fmt.format("Zone", "Timestamp", "Error"))
                first_error = False

            r = {}
            for key in result:
                if result[key] is None:
                    r[key] = "None"
                else:
                    r[key] = result[key]

            print(err_fmt.format(
                r['location'],
                r['timestamp'],
                r['error']
            ))


def main():
    """The main function.  Run argument parsing, make predictions, and present results."""
    parser = argparse.ArgumentParser(
        description=f"{name} v{version}: A program that determines the fault type and offending cavity based on a"
                    " waveform data from a C100 fault event", epilog="Pluggable models are no longer available.")
    subparsers = parser.add_subparsers(help='commands', dest='subparser_name')
    describe_model = subparsers.add_parser('describe', help='Describe the embedded model')
    describe_model.add_argument('-v', '--verbose', action='store_true', help='Print verbose model info')
    analyze = subparsers.add_parser("analyze", help='Analyze a fault event')
    analyze.add_argument("-o", "--output", help="Specify the output format (default: table)",
                         default="table", dest='output')
    analyze.add_argument("-n", "--no-header", help="Do not include a header in the output (only for -o=table)",
                         default=False, dest='no_header', action='store_true')
    analyze.add_argument("events", nargs='+', help="The path to the fault event directory", default=None)

    # Parse command line arguments.  Print out the certified name/version if none is specified
    args = parser.parse_args()

    if args.subparser_name is None:
        print("%s v%s" % (name, version))
        exit(0)
    elif args.subparser_name == 'describe':
        from .model.model import Model, print_model_description
        model = Model()
        print_model_description(args.verbose)
        exit(0)
    elif args.subparser_name == 'analyze':

        # Call the appropriate model and get the results
        results = run_model(args.events)
        # None implies that the model had some sort of a problem
        if results is None:
            exit(1)
        else:
            if args.output == "json":
                # # The model does not include it's name on the response.  Add it to each result.
                # for i in range(0, len(results['data'])):
                #     results['data'][i]['model'] = cfg['model']
                # A dictionary prints out _VERY_ similarly to JSON, but maybe not exactly.  Just use the json.dump.
                print(json.dumps(results))
            else:
                # If the user doesn't request a support format print out a table
                # print_results_table(results['data'], cfg, header=(not args.no_header))
                print_results_table(results['data'], header=(not args.no_header))
        exit(0)
    else:
        print(f'Unrecognized subcommand "{args.subparser_name}')


if __name__ == "__main__":
    main()
