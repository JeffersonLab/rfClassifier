from unittest import TestCase
# from .concrete_model import Model
from base_model import BaseModel

import os
import pandas as pd


class Model(BaseModel):
    """A generic concrete implementation of BaseModel that allows for testing of non-abstract methods"""

    def describe(self):
        pass

    def analyze(self):
        pass


def check_list_equal(list1, list2):
    return len(list1) == len(list2) and sorted(list1) == sorted(list2)


class TestBaseModel(TestCase):
    # Example of a simplified event.  Allows for easier checking that the data parsing is correct
    simple_event_path = os.path.join(os.path.dirname(__file__), "test-data", "short-test")

    # Example that has the proper event path starting at the date directory.  One with good control modes, one with bad
    good_mode_path = os.path.join(os.path.dirname(__file__), "test-data", "good-cavity-mode", "2018_10_04", "052657.4")
    bad_mode_path = os.path.join(os.path.dirname(__file__), "test-data", "bad-cavity-mode", "2018_10_04", "052659.4")

    # Examples of the normal data file we will be working with
    good_path = os.path.join(os.path.dirname(__file__), "test-data", "good-example")
    good_path_meta = os.path.join(os.path.dirname(__file__), "test-data", "good-example-meta")

    # Contain proper capture files, but have problems which waveforms are present
    missing_path = os.path.join(os.path.dirname(__file__), "test-data", "missing-waveforms")
    duplicate_path = os.path.join(os.path.dirname(__file__), "test-data", "duplicate-waveforms")

    # Has missing or duplicate capture files
    missing_cfs_path = os.path.join(os.path.dirname(__file__), "test-data", "missing-cfs")
    duplicate_cfs_path = os.path.join(os.path.dirname(__file__), "test-data", "duplicate-cfs")

    # Has a mismatched Time column between R1P1 and R1P2
    mismatched_time_path = os.path.join(os.path.dirname(__file__), "test-data", "mismatched-times")
    bad_time_interval_path = os.path.join(os.path.dirname(__file__), "test-data", "bad-time-interval")

    def test_get_data(self):
        exp_df = pd.DataFrame({"Time": [0.1, 0.2, 0.3],
                               "1_wf1": [1, 4, 18], "1_wf2": [36, -17, 5],
                               "2_wf1": [21, 24, 218], "2_wf2": [236, -217, 25],
                               "3_wf1": [31, 34, 318], "3_wf2": [336, -317, 35],
                               "4_wf1": [41, 44, 418], "4_wf2": [436, -417, 45],
                               "5_wf1": [51, 54, 518], "5_wf2": [536, -517, 55],
                               "6_wf1": [61, 64, 618], "6_wf2": [636, -617, 65],
                               "7_wf1": [71, 74, 718], "7_wf2": [736, -717, 75],
                               "8_wf1": [81, 84, 818], "8_wf2": [836, -817, 85]
                               })

        mod = Model(TestBaseModel.simple_event_path)
        mod.parse_event_dir()
        result_df = mod.get_event_df()

        self.assertTrue(exp_df.equals(result_df))
        self.assertTrue(check_list_equal(exp_df.columns, result_df.columns))
        # self.assertTrue(exp_df.columns == result_df.columns)

    def test_validate_capture_file_counts(self):
        # Should work
        mod = Model(TestBaseModel.good_path)
        mod.validate_capture_file_counts()

        # Test out failure cases
        mod = Model(TestBaseModel.missing_cfs_path)
        self.assertRaises(ValueError, mod.validate_capture_file_counts)

        mod = Model(TestBaseModel.duplicate_cfs_path)
        self.assertRaises(ValueError, mod.validate_capture_file_counts)

    def test_validate_capture_file_waveforms(self):
        # This should work and not raise an exception
        mod = Model(TestBaseModel.good_path)
        mod.parse_event_dir()
        mod.validate_capture_file_waveforms()

        # This should work and not raise an exception
        mod = Model(TestBaseModel.good_path_meta)
        mod.parse_event_dir()
        mod.validate_capture_file_waveforms()

        # Check that the validation raises an exception on files missing waveforms
        mod = Model(TestBaseModel.missing_path)
        mod.parse_event_dir()
        self.assertRaises(ValueError, mod.validate_capture_file_waveforms)

        # Check that the validation raises an exception on files with duplicate waveforms
        mod = Model(TestBaseModel.duplicate_path)
        mod.parse_event_dir()
        self.assertRaises(ValueError, mod.validate_capture_file_waveforms)

    def test_validate_waveform_times(self):
        # This should work
        mod = Model(TestBaseModel.good_path)
        mod.validate_waveform_times()

        # This should work
        mod = Model(TestBaseModel.good_path_meta)
        mod.validate_waveform_times()

        # This should raise a ValueError since two of the files have different time columns
        mod = Model(TestBaseModel.mismatched_time_path)
        self.assertRaises(ValueError, mod.validate_waveform_times)

        # This should raise a ValueError since all of the files have the same Time series that is too long
        mod = Model(TestBaseModel.bad_time_interval_path)
        self.assertRaises(ValueError, mod.validate_waveform_times)

    def test_validate_cavity_modes(self):
        # The time associated with this event should have all good control modes
        mod = Model(TestBaseModel.good_mode_path)
        mod.validate_cavity_modes()

        # The time for this should have at least one bad control mode and will raise and exception
        mod = Model(TestBaseModel.bad_mode_path)
        self.assertRaises(ValueError, mod.validate_cavity_modes)
