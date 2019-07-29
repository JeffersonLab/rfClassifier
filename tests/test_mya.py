from unittest import TestCase
import unittest
import mya
from datetime import datetime

class TestMya(TestCase):
    def test_get_json(self):
        exp_json = {
            'datatype': 'DBR_DOUBLE',
            'datasize': 1,
            'datahost': 'hstmya1',
            'data': {'d': '2017-12-27T12:07:07', 'v': 7.69905}
        }
        result_json = mya.get_json(mya.__myquery_url__ + "/point?c=R123GSET&t=2018-01-01+00:00:00&m=history&f=&v=")
        self.assertDictEqual(exp_json, result_json, "Didn't receive expected response from myaweb")

        # Check that wrong content types raises
        self.assertRaises(ValueError, mya.get_json, url="http://ced.acc.jlab.org/elem/0L03-4?out=xml")

    def test_get_pv_value(self):
        exp = 7.69905
        d = datetime(2018,1,1,0,0,0,0)
        result = mya.get_pv_value(PV='R123GSET', datetime=d, deployment='history')
        self.assertAlmostEqual(exp, result, delta=0.0000001)

        # Check that bad PV name raises error
        self.assertRaises(ValueError, mya.get_pv_value, PV="R1234_bad_name", datetime=d, deployment='ops')

        # Check that bad deployment name raises error
        self.assertRaises(ValueError, mya.get_pv_value, PV="R123GSET", datetime=d, deployment='bad_deployment_name')


if __name__ == '__main__':
    unittest.main()