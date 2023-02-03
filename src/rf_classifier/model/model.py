import os
import platform
import sys
import math
from datetime import datetime
import json
import yaml
from typing import Any, Dict, Optional, Tuple, List

import numpy as np
import pandas as pd
from rfwtools.utils import get_signal_names
from rfwtools.example import Example
from rfwtools.example_validator import ExampleValidator
from rfwtools.extractor.windowing import window_extractor
from rfwtools.config import Config
import onnxruntime as rt
from sklearn.preprocessing import StandardScaler



from .. import utils

app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
"""The base directory of this model application."""

lib_dir = os.path.join(app_dir, 'lib')
"""The directory where python code and pickle files containing tsfresh models, etc. can be found."""


def get_model_description() -> Dict[str, Any]:
    """Parses the description.yaml file associated with this model and returns the resulting dictionary"""

    desc_file = os.path.join(os.path.dirname(__file__), "model_files", "description.yaml")
    if not os.path.exists(desc_file):
        raise FileNotFoundError(f"File not found - {desc_file}")
    else:
        with open(desc_file, "r") as f:
            desc = yaml.safe_load(f.read())
            if desc is None:
                raise RuntimeError(f"Error parsing {desc_file}")
    return desc


def print_model_description(verbose: bool):
    """Function for reading and print a model's description based on it's description.yaml file.

    Args:
        verbose (bool): Whether to print out the detailed information of the model

    Returns:
        None:  Prints out description or relevant error messages.
    """

    desc = get_model_description()
    description = f"""
Model ID:      {desc['id']}
Release Date:  {desc['releaseDate']}
Cavity Labels: {desc['cavityLabels']}
Fault Labels:  {desc['faultLabels']}
Training Data: {desc['trainingData']}
Brief:         {desc['brief']}
"""
    if verbose:
        description += os.linesep + f"Details:       {desc['details']}"
    print(description)


def softmax(x: np.array) -> Tuple[int, List[float]]:
    """Calculates the softmax output of a model and returns the index of the maximum value (predicted class)."""
    dist = np.exp(x) / np.sum(np.exp(x))
    y = np.argmax(dist)
    return int(y), dist


def standard_scaling(df: pd.DataFrame, fill: float = 0.0) -> pd.DataFrame:
    """This is like sklearn's StandardScaler, except that constant signals are replaced with an arbitrary constant.

    This transforms the DataFrame in place.
    """
    scaler = StandardScaler(copy=True, with_mean=True, with_std=True)
    df = df.copy()
    for i in range(len(df.columns)):
        signal = df.iloc[:, i].values.reshape(-1, 1)
        if np.min(signal) == np.max(signal):
            df.iloc[:, i] = [fill] * len(signal)
        else:
            df.iloc[:, i] = scaler.fit_transform(signal)
    return df


class Model:
    """
    This model uses CNN/LSTM deep learning models to identify the faulted cavity and fault type of a C100 event.

    This model is based on work done by Chris Tennant, Lasitha Vidyaratne, Md. Monibor Rahman, Tom Powers, etc. and
    represents an improved model used to identify which cavity and fault type is associated with a C100 fault event.
    Any individual cavity can be identified as the offending cavity.  Any collection of multiple cavities faulting at
    the same time are given the generic label of 'multiple'.  The following fault types may be identified by the model:
    Controls Fault, E_Quench, Heat Riser Choke, Microphonics, Quench_100ms, Quench_3ms, Single Cav Turn off, and
    Multi-cav Turn off.  The fault model is no longer trained on Multi Cav turn off, as we use only the cavity model
    to identify that condition.

    Additional documentation is available in the package docs folder.
    """

    def __init__(self):
        """Create a Model object.  This performs all data handling, validation, and analysis."""
        self.model_description: Dict[str, Any] = get_model_description()
        self.model_name: str = self.model_description['name']
        self.model_version: str = self.model_description['version']

        # Make sure we do not have a trailing slash to muck up processing later.
        self.event_dir: Optional[str] = None
        self.zone_name: Optional[str] = None
        self.fault_time: Optional[str] = None

        self.example: Example = None
        self.validator: ExampleValidator = ExampleValidator()
        self.common_features_df: pd.DataFrame = None

        self.cavity_onnx_session: rt.InferenceSession = rt.InferenceSession(os.path.join(os.path.dirname(__file__),
                                                                                         'model_files',
                                                                                         'cavity_model.onnx'))
        self.fault_onnx_session: rt.InferenceSession = rt.InferenceSession(os.path.join(os.path.dirname(__file__),
                                                                                        'model_files',
                                                                                        'fault_model.onnx'))

    def update_example(self, path: str):
        """Updates the currently loaded example to reflect the new path"""

        if not path.startswith(os.sep):
            raise ValueError("Path to fault-data must be absolute")

        # Update info in the model for the currently loaded example
        path = path.rstrip(os.sep)
        zone_name, fault_time = utils.path_to_zone_and_timestamp(path)
        self.event_dir = path
        self.zone_name = zone_name
        self.fault_time = fault_time

        # Split up the path into it's constituent pieces
        tokens = path.split(os.sep)
        dt = datetime.strptime(f"{tokens[-2]} {tokens[-1]}", "%Y_%m_%d %H%M%S.%f")
        zone = tokens[-3]

        # Save the root data path into the rfwtools configuration.  Windows is weird, C: doesn't get handled correctly.
        if platform.system() == "Windows":
            data_dir = os.path.join(tokens[0], os.sep, *tokens[1:-3])
        else:
            data_dir = os.path.join(os.path.sep, *tokens[:-3])
        Config().data_dir = data_dir

        # Update the example the model is currently loading
        self.example = Example(zone=zone, dt=dt, cavity_conf=math.nan, fault_conf=math.nan, cavity_label="",
                               fault_label="", label_source="")

    def analyze(self, deployment: str = 'ops') -> Dict[str, Any]:
        """A method that performs some analysis and classifies the fault event by cavity number and fault type.

        This method validates that the capture files and waveform data in event_dir are in the expected format and
        internally consistent.  First the cavity label is determined by the cavity model.  Should this return a
        "multiple" cavity label, the no fault type label determination is made.  Instead, a fault type label of
        "Multi Cav Turn Off" with the same confidence as the cavity label.

        In addition to the classification label output, this method should include information about the confidence
        of those classifications and list which fault event is being analyzed.  Confidence numbers should be given
        on the range [0,1] with lower numbers implying more uncertainty and higher numbers implying greater
        certainty.

        Arguments:
            deployment:

            Returns:
                dict: A dictionary containing the results of the analysis.  Detailed key/value information given in the
                table below.

            +---------------------+------------+-----------------------------------------------------------------+
            | Key                 | Value Type | Value Descriptions                                              |
            +=====================+============+=================================================================+
            | "location"          | str        | Zone of the fault event. (e.g. "1L22")                          |
            +---------------------+------------+-----------------------------------------------------------------+
            | "timestamp"         | str        | Timestamp of the fault event, (e.g. "2019-12-25 01:23:45.6")    |
            +---------------------+------------+-----------------------------------------------------------------+
            | "cavity-label"      | str        | Label of the cavity that faulted (e.g., "1")                    |
            +---------------------+------------+-----------------------------------------------------------------+
            | "cavity-confidence" | float      | Number between [0,1] representing cavity label confidence       |
            +---------------------+------------+-----------------------------------------------------------------+
            | "fault-label"       | str        | Label of the identified fault type (e.g., quench)               |
            +---------------------+------------+-----------------------------------------------------------------+
            | "fault-confidence"  | float      | Number between [0,1] representing fault type label confidence   |
            +---------------------+------------+-----------------------------------------------------------------+
        """
        # Check that the data we're about to analyze meets any preconditions for our model
        self.validate_data(deployment)

        # Preprocess the data before model inference
        self.preprocess_data()

        # Analyze the data to determine which cavity caused the fault.
        cav_results = self.get_cavity_label()

        # A value of cavity-label '0' corresponds to a multi-cavity event.  In this case the fault analysis is
        # unreliable and we should short circuit and report only a multi-cavity fault type (likely someone
        # performing a zone wide operation triggering a "fault").  Use the cavity confidence since it is the
        # prediction we're basing this on.
        fault_results = {'fault-label': 'Multi Cav turn off', 'fault-confidence': cav_results['cavity-confidence']}
        if cav_results['cavity-label'] != 'multiple':
            fault_results = self.get_fault_type_label(int(cav_results['cavity-label']))

        return {
            'location': self.example.event_zone,
            'timestamp': self.example.event_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-5],
            'cavity-label': cav_results['cavity-label'],
            'cavity-confidence': float(cav_results['cavity-confidence']),
            'fault-label': fault_results['fault-label'],
            'fault-confidence': float(fault_results['fault-confidence']),
            'model': f"{self.model_name}_v{self.model_version.replace('.', '_')}"
        }

    def preprocess_data(self):
        """This method preprocesses the data in preparation for model input.  Updates self.common_features_df."""
        # Fault and cavity models use same data and features.  Get that now.
        signals = get_signal_names(cavities=['1', '2', '3', '4', '5', '6', '7', '8'],
                                   waveforms=['GMES', 'GASK', 'CRFP', 'DETA2'])

        # We need to crop, downsample, then do z-score.  Any constant values are set to 0.001 manually.
        num_resample = 4096
        num_meta_columns = 8
        self.common_features_df = window_extractor(self.example, signals=signals, windows={'pre-fault': -1533.4},
                                                   n_samples=7680, standardize=False, downsample=True,
                                                   ds_kwargs={'num': num_resample})

        # The extractor makes a row per requested window plus some metadata.  Columns are named
        # Sample_<sample_num>_<cav_num>_<signal>, and go Sample_1_1_GMES, Sample_2_1_GMES, ..., Sample_1_1_GASK, ....
        # We want to change this so that each column is all of the samples for 1_GMES, 1_GASK, ... as in the signal
        # order above.
        self.common_features_df = pd.DataFrame(
            self.common_features_df.iloc[0, num_meta_columns:].values.reshape(len(signals), -1).T, columns=signals)

        self.common_features_df = standard_scaling(self.common_features_df, fill=0.001)

    def validate_data(self, deployment='ops'):
        """Check that the event directory and it's data is of the expected format.

        This method inspects the event directory and raises an exception if a problem is found.  The following aspects
        of the event directory and waveform data are validated.
        - All eight cavities are represented by exactly one capture file
        - All of the required waveforms are represented exactly once
        - All of the capture files use the same timespan and have constant sampling intervals
        - All of the cavity are in the appropriate control mode (GDR I/Q => 4 or SELAP => 64)

        Args:
            deployment (str):  Which MYA deployment to use when validating cavity operating modes.

        Returns:
            None: Subroutines raise an exception if an error condition is found.
        """
        self.validator.set_example(self.example)

        # Don't just use the built in validate_data method as this needs to be future proofed against C100 firmware
        # upgrades.  This upgrade will result in a new mode SELAP (R...CNTL2MODE == 64).
        self.validator.validate_capture_file_counts()
        self.validator.validate_capture_file_waveforms()

        # Many of these examples will have some amount of rounding error.
        self.validator.validate_waveform_times(min_end=10.0, max_start=-1534.0, step_size=0.2)
        self.validator.validate_cavity_modes(mode=(4, 64), deployment=deployment)
        self.validator.validate_zones()

    def make_prediction(self, sess):
        """Use an ONNX InferenceSession to make a prediction based on the current example's features"""
        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[0].name

        # Model outputs a list of 2D arrays.  Only one prediction, so pull it out of the larger structure for easier
        # work
        prediction = sess.run([label_name],
                              {input_name: self.common_features_df.values.reshape(1, -1, 32).astype(np.float32)})
        prediction = prediction[0][0]

        # The model does not return a probability distribution or a cavity id, but a 9D output.  Run softmax on it to
        # get out prediction and "probability"
        idx, confs = softmax(prediction)
        confidence = confs[idx]

        return idx, confidence

    def get_cavity_label(self):
        """Loads the underlying cavity model and performs the predictions based on the common_features_df.

            Returns:
                A dictionary with format {'cavity-label': <string_label>, 'cavity-confidence': <float in [0,1]>}"
        """
        # Load the cavity model and make a prediction about which cavity faulted
        cavity_id, cavity_confidence = self.make_prediction(self.cavity_onnx_session)

        # Convert the results from an int to a human-readable string
        if cavity_id == 0:
            cavity_id = 'multiple'
        else:
            # The cavity_id int corresponds to the actual cavity number if 1-8
            cavity_id = str(cavity_id)

        return {'cavity-label': cavity_id, 'cavity-confidence': cavity_confidence}

    def get_fault_type_label(self, cavity_number):
        """Loads the underlying fault type model and performs the predictions based on the common_features_df.

            Args:
                cavity_number (int): The number of the cavity (1-8) that caused the fault.

            Returns:
                A dictionary with format {'fault-label': <string_label>, 'fault-confidence': <float in [0,1]>}"
        """
        # Make sure we received a valid cavity number
        self.assert_valid_cavity_number(cavity_number)

        # Load fault type model and make a prediction on the current example's features
        fault_idx, fault_confidence = self.make_prediction(self.fault_onnx_session)

        # Get the fault name and probability associated with that index
        fault_names = ["Quench_100ms", "Quench_3ms", "E_Quench", "Heat Riser Choke", "Microphonics", "Controls Fault",
                       "Single Cav Turn off"]
        fault_name = fault_names[fault_idx]

        return {'fault-label': fault_name, 'fault-confidence': fault_confidence}

    @staticmethod
    def assert_valid_cavity_number(cavity_number):
        """Throws an exception if the supplied integer is not a valid cavity number.

            Args:
                cavity_number (int): The cavity number to evaluate.

            Raises:
                TypeError: if cavity_number is not an int
                ValueError: if cavity_number is not in range [1,8]
        """

        # Check that we have a valid cavity number
        if not isinstance(cavity_number, int):
            raise TypeError("cavity_number must be of type int")
        if not (cavity_number <= 8 or cavity_number >= 1):
            raise ValueError("cavity_number must be within span of [1,8]")


def main():
    if len(sys.argv) == 1:
        # Print an error/help message
        print("Error: Requires a single argument - the path to an RF waveform event folder")
        exit(1)
    else:
        # Analyze the faults that were passed
        data = []
        # The first argument is the main of this python script
        sys.argv.pop(0)

        # Iterate over each path and analyze the event
        mod = None
        for path in sys.argv:
            if mod is None:
                mod = Model(path)
            else:
                mod.update_example(path)

            # Determine the zone and timestamp of the event from the path.  If the path is poorly formatted, this will
            # raise an exception
            zone = None
            timestamp = None
            error = None
            try:
                (zone, timestamp) = utils.path_to_zone_and_timestamp(path)
            except Exception as ex:
                # ex = sys.exc_info()
                # ex[1] is the exception message
                error = "{}".format(repr(ex))

            if error is None:
                # Try to analyze the fault.  If any of the validation routines fail, they will raise an exception.
                try:
                    result = mod.analyze()
                    data.append(result)
                except Exception as ex:
                    # ex = sys.exc_info()

                    result = {
                        # ex[1] is the exception message
                        'error': r'{}'.format(repr(ex)),
                        'location': zone,
                        'timestamp': timestamp
                    }
                    data.append(result)
            else:
                # If we had trouble parsing the location/timestamp info, don't try to analyze the fault.
                data.append({'error': error, 'path': path})

        print(json.dumps({'data': data}))


if __name__ == "__main__":
    main()
