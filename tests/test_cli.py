import unittest
import subprocess
import os

rfc = os.path.join(os.path.dirname(__file__), "..", "bin", "rf_classifier.bash")
test_data = os.path.join(os.path.dirname(__file__), "test-data")

class TestCLI(unittest.TestCase):
    def test_cli_blank(self):
        process = subprocess.run([rfc], stdout=subprocess.PIPE, universal_newlines=True)
        self.assertRegex(process.stdout, "rf_classifier v\d.\d", "No args should print app name and version")

    def test_cli_describe(self):
        exp = """Model ID: .*
Release Date:  .*
Cavity Labels: .*
Fault Labels:  .*
Training Data: .*
Brief:         .*
"""
        process = subprocess.run([rfc, 'describe'], stdout=subprocess.PIPE, universal_newlines=True)
        self.assertRegex(process.stdout, exp, "Description does not meet basic format")

    def test_cli_analyze_table(self):
        exp = """Cavity     Fault               Zone     Timestamp              Model                Cav-Conf Fault-Conf
6          Single Cav Turn off 1L25     2023-02-01 21:00:26.1  cnn_lstm_v1_0        0.96     0.82    
"""

        process = subprocess.run([rfc, 'analyze', f"{test_data}/good-example/1L25/2023_02_01/210026.1"],
                                 stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(process.stdout, exp, "Unexpected analysis results")

    def test_cli_analyze_json(self):
        exp = """{\"data\": [{\"location\": \"1L25\", \"timestamp\": \"2023-02-01 21:00:26.1\", \"cavity-label\": \"6\", \"cavity-confidence\": 0.9596626162528992, \"fault-label\": \"Single Cav Turn off\", \"fault-confidence\": 0.8224388957023621, \"model\": \"cnn_lstm_v1_0\"}]}
"""
        process = subprocess.run([rfc, 'analyze', "-o", "json", f"{test_data}/good-example/1L25/2023_02_01/210026.1"],
                                 stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(process.stdout, exp, "Unexpected analysis results")

    def test_cli_analyze_table_error(self):
        exp = """Zone     Timestamp              Error
1L25     2018-10-05 04:44:08.2  Missing capture file for zone '3'
"""

        process = subprocess.run([rfc, 'analyze', f"{test_data}/missing-cfs/1L25/2018_10_05/044408.2"],
                                 stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(process.stdout, exp, "Unexpected error message")

    def test_cli_analyze_json_error(self):
        exp = """{\"data": [{\"error\": \"Missing capture file for zone '3'\", \"location\": \"1L25\", \"timestamp\": \"2018-10-05 04:44:08.2\"}]}
"""

        process = subprocess.run([rfc, 'analyze', '-o', 'json', f"{test_data}/missing-cfs/1L25/2018_10_05/044408.2"],
                                 stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(process.stdout, exp, "Unexpected error message")
