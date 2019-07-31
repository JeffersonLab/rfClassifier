from unittest import TestCase
import unittest
import os
import main

test_dir = os.path.dirname(__file__)


class TestMain(TestCase):
    def test_parse_config_file(self):
        # Test that a basic use case without a default model works
        exp = {
            "some_key": "some_value",
            "models_dir": "/some/junk/dir",
            "default_model": None,
            "model": None
        }
        result = main.parse_config_file(os.path.join(test_dir, 'files', 'test_config_w_models_dir.yaml'))
        self.assertDictEqual(exp, result)

        # Test that a basic use case without an external configuration directory gets the default
        exp = {
            "some_key": "some_value",
            "models_dir": os.path.join('cs','certified', 'apps', "rf_classifier", "0.1", 'models'),
            "default_model": "my_test_model",
            'model': "my_test_model"
        }
        result = main.parse_config_file(os.path.join(test_dir, 'files', 'test_config_wo_models_dir.yaml'))
        self.assertDictEqual(exp, result)


if __name__ == '__main__':
    unittest.main()
