from unittest import TestCase
import unittest
import os
import utils
from datetime import datetime

class TestUtils(TestCase):
    def test_path_to_datetime(self):
        path = os.path.join("some", "path", "2018_05_01", "012345.6")
        exp = datetime(year=2018, month=5, day=1, hour=1, minute=23, second=45, microsecond=600000)
        self.assertEqual(exp, utils.path_to_datetime(path))

        self.assertRaises(ValueError, utils.path_to_datetime, os.path.join("some", "path", "20178-05-01", "00:03:50"
                                                                                                          ".7289"))


if __name__ == '__main__':
    unittest.main()