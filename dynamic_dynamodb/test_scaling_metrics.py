# -*- coding: utf-8 -*-
""" Testing the Dynamic DynamoDB scaling methods """
import unittest

from dynamic_dynamodb.core.table import scale_reader


class TestScaleReader(unittest.TestCase):
    """ Test the scale reader method """

    def __init__(self):
        self.value = {0: 0, 0.25: 5, 0.5: 10, 1: 20, 2: 50, 5: 100}

    def test_scale_reader_zero(self):
        """ Ensure that using a current_value of zero returns zero """
        result = scale_reader(self.value, 0, 80)
        self.assertEqual(result, 0)

    def test_scale_reader_lower_threshold(self):
        """
        Ensure that when current_value is above zero but
        before the lowest threshold zero is returned
        """
        result = scale_reader(self.value, 0.1, 80)
        self.assertEquals(result, 0)

    def test_scale_reader_upper_threshold(self):
        """
        Ensure that when current_value is above the highest
        threshold the highest scaling configured is used
        """
        result = scale_reader(self.value, 7, 80)
        self.assertEquals(result, 100)

    def test_scale_reader_boundary_value_lower(self):
        """
        Ensure that correct scaling is used when current_value
        is on the lower end of a boundary
        """
        result = scale_reader(self.value, 1, 80)
        self.assertEquals(result, 10)

    def test_scale_reader_boundary_value_upper(self):
        """
        Ensure that correct scaling is used when current_value
        is on the upper end of a boundary
        """
        result = scale_reader(self.value, 1.01, 80)
        self.assertEquals(result, 20)

    def test_scale_reader_default_scale(self):
        """
        Ensure that if no provision_increase_scale is provided
        the default_scale_with value is used
        """
        result = scale_reader({}, 5, 80)
        self.assertEquals(result, 80)

if __name__ == '__main__':
    unittest.main(verbosity=2)
