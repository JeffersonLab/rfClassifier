import datetime
import unittest
import warnings

from unittest import TestCase
import os
import sys

import numpy as np

from . import testing_utils

# Put the lib dir at the front of the search path.  Makes the sys.path correct regardless of the context this test is
# run.
app_root = os.path.join(os.path.dirname(os.path.dirname(__file__)))
app_lib = os.path.join(app_root, "lib")
sys.path.insert(0, app_lib)
from rf_classifier.model.model import Model


class TestModel(TestCase):

    def test_analyze(self):
        # I'm comparing strings now, not Dict directly.  Need to see the output without truncation.
        self.maxDiff = None
        # Context manager resets warnings filters to default after code section exits
        # I've spent tons of time trying to figure out why the analyze method and specifically it call of
        # sklearn.externals.joblib.load(...) produces RuntimeWarnings for numpy.ufunc binary incompatibility _ONLY_ when
        # running from unittest.  I give up.  Just suppress these warnings.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "can't resolve package from __spec__ or __package__, "
                                              "falling back on __name__ and __path__")
            warnings.filterwarnings("ignore", "numpy.ufunc size changed, may indicate binary incompatibility. "
                                              "Expected 192 from C header, got 216 from PyObject")
            warnings.filterwarnings("ignore", "numpy.ufunc size changed, may indicate binary incompatibility. "
                                              "Expected 216, got 192")
            mod = None
            failed = 0
            test_file = os.path.join(app_root, 'tests', 'test_set.txt')
            test_results_file = os.path.join(app_root, 'tests', 'test_results.txt')
            test_set = testing_utils.TestSet(test_file)
            num_tests = len(test_set.get_events())
            print(f"Testing {num_tests} events.  This may take ~{num_tests * 3} seconds.")

            msgs = []
            ts_new_df = test_set.test_set_df.copy()
            for test_event in test_set.get_events():
                event = testing_utils.EventData(zone=test_event['zone'], timestamp=test_event['timestamp'])

                try:
                    event.get_event_data()
                except Exception as exc:
                    failed += 1
                    msgs.append("## Failed to get data for test.")
                    msgs.append(exc)

                    continue

                expect = test_event['expected']
                if expect['cavity-label'] == '0':
                    expect['cavity-label'] = 'multiple'
                path = event.event_dir

                if mod is None:
                    mod = Model()
                mod.update_example(path)

                # The history archiver has everything, except recent data.  ops archiver has recent data, but not
                # anything more than maybe two years old.
                deployment = 'history'
                if datetime.datetime.now() - event.timestamp < datetime.timedelta(days=91):
                    deployment = 'ops'

                # Some test cases are intended to trigger exceptions, handle them differently than the "good" cases
                if expect['throws']:
                    try:
                        mod.analyze(deployment=deployment)
                    except:
                        pass
                    else:
                        z_match = ts_new_df.zone == test_event['zone']
                        t_match = ts_new_df.time == test_event['timestamp']
                        ts_new_df.loc[z_match & t_match, 'throws'] = False

                        failed += 1
                        msgs.append(f"## FAIL: Event {test_event['zone']} - {test_event['timestamp']} should"
                              f" have thrown exception but did not")

                else:
                    try:
                        result = mod.analyze(deployment=deployment)
                    except Exception as e:
                        failed += 1
                        msgs.append(f"## FAIL: Event {test_event['zone']} - {test_event['timestamp']} exception during analysis. {e}")

                        z_match = ts_new_df.zone == test_event['zone']
                        t_match = ts_new_df.time == test_event['timestamp']
                        ts_new_df.loc[z_match & t_match, 'throws'] = True
                        continue

                    # The test set file only has four decimal places.
                    result['cavity-confidence'] = str(np.round(result['cavity-confidence'] * 100, 2))
                    result['fault-confidence'] = str(np.round(result['fault-confidence'] * 100, 2))

                    # Update the 'new' test set with these results
                    z_match = ts_new_df.zone == test_event['zone']
                    t_match = ts_new_df.time == test_event['timestamp']
                    ts_new_df.loc[z_match & t_match, 'cav_pred'] = result['cavity-label']
                    ts_new_df.loc[z_match & t_match, 'fault_pred'] = result['fault-label']
                    ts_new_df.loc[z_match & t_match, 'cav_conf'] = result['cavity-confidence']
                    ts_new_df.loc[z_match & t_match, 'fault_conf'] = result['fault-confidence']

                    # Remove the throws entry from expected since the result won't have this
                    del expect['throws']
                    try:
                        self.assertDictEqual(expect, result)
                    except Exception as e:
                        failed += 1
                        msgs.append(f"## FAIL: Event {test_event['zone']} - {test_event['timestamp']} had unexpected results. {e}")

                try:
                    event.delete_event_data()
                except Exception as e:
                    msgs.append("## Error deleting data - {e}")

            # Convert back to the numeric version.
            ts_new_df.loc[ts_new_df['cav_pred'] == 'multiple', 'cav_pred'] = '0'

            # Write out the results of the test in a similar fashion as the test set
            ts_new_df.to_csv(test_results_file, sep='\t', index=False)

            if failed > 0:
                msgs = [f"Failed {failed} example tests"] + msgs
                self.fail('\n'.join(msgs))

    def test_model_validation_bad(self):
        model = Model()

        data_dir = os.path.dirname(__file__) + "/test-data"
        test_paths = [
            f'{data_dir}/bad-cavity-mode/test_zone/2018_10_04/052659.4',
            f'{data_dir}/bad-time-interval/test_zone/2018_10_05/044556.2',
            f'{data_dir}/duplicate-cfs/test_zone/2018_10_05/044408.2',
            f'{data_dir}/duplicate-waveforms/test_zone/2018_10_05/044556.2',
            f'{data_dir}/mismatched-times/test_zone/2018_10_05/044556.2',
            f'{data_dir}/missing-cfs/test_zone/2018_10_05/044408.2',
            f'{data_dir}/missing-waveforms/test_zone/2018_10_05/044556.2',
            f'{data_dir}/short-test/test_zone/0000_00_00/000000.0'
        ]

        msgs = []
        tests_failed = 0
        for p in test_paths:
            try:
                model.update_example(p)
                model.analyze()
            except:
                pass
            else:
                tests_failed += 1
                msgs.append(f"## FAIL: '{p}' should have raise exception but didn't")

        if tests_failed > 0:
            msgs = [f"## FAILED {tests_failed} 'bad' data validation tests"] + msgs
            self.fail('\n'.join(msgs))

    def test_model_validation_good(self):
        model = Model()

        data_dir = os.path.dirname(__file__) + "/test-data"
        test_paths = [
            f'{data_dir}/good-cavity-mode/1L25/2023_02_01/210026.1',
            f'{data_dir}/good-example/1L25/2023_02_01/210026.1',
            f'{data_dir}/good-example-meta/1L25/2023_02_01/210026.1',
        ]

        msgs = []
        tests_failed = 0
        for p in test_paths:
            try:
                model.update_example(p)
                model.analyze()
            except Exception as ex:
                msgs.append(f"## FAIL: '{p}' raised exception\n   {ex}")
                tests_failed += 1

        if tests_failed > 0:
            msgs = [f"## FAILED {tests_failed} 'good' data validation tests"] + msgs
            self.fail('\n'.join(msgs))


if __name__ == '__main__':
    unittest.main()
