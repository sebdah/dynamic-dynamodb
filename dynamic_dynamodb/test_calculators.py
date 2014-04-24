# -*- coding: utf-8 -*-
""" Testing the Dynamic DynamoDB calculators """
import unittest

import calculators


class TestCalculators(unittest.TestCase):
    """ Test the Dynamic DynamoDB calculators """

    def test_decrease_reads_in_percent(self):
        """ Ensure that a regular decrease works """
        result = calculators.decrease_reads_in_percent(200, 90, 1, 'test')
        self.assertEqual(result, 20)

    def test_decrease_reads_in_percent_hit_min_value(self):
        """ Check that min values are honoured """
        result = calculators.decrease_reads_in_percent(20, 50, 15, 'test')
        self.assertEqual(result, 15)

    def test_decrease_reads_in_percent_more_than_100_percent(self):
        """ Handle decreases of more that 100% """
        result = calculators.decrease_reads_in_percent(20, 120, 1, 'test')
        self.assertEqual(result, 1)

    def test_decrease_reads_in_percent_type_current_provisioning(self):
        """ Check that current_provisioning only takes an int """
        self.assertRaises(
            TypeError,
            calculators.decrease_reads_in_percent,
            '100',
            90,
            1,
            'test')

    def test_decrease_writes_in_percent(self):
        """ Ensure that a regular decrease works """
        result = calculators.decrease_writes_in_percent(200, 90, 1, 'test')
        self.assertEqual(result, 20)

    def test_decrease_writes_in_percent_hit_min_value(self):
        """ Check that min values are honoured """
        result = calculators.decrease_writes_in_percent(20, 50, 15, 'test')
        self.assertEqual(result, 15)

    def test_decrease_writes_in_percent_more_than_100_percent(self):
        """ Handle decreases of more that 100% """
        result = calculators.decrease_writes_in_percent(20, 120, 1, 'test')
        self.assertEqual(result, 1)

    def test_decrease_writes_in_percent_type_current_provisioning(self):
        """ Check that current_provisioning only takes an int """
        self.assertRaises(
            TypeError,
            calculators.decrease_writes_in_percent,
            '100',
            90,
            1,
            'test')

    def test_decrease_reads_in_units(self):
        """ Ensure that a regular decrease works """
        result = calculators.decrease_reads_in_units(200, 90, 1, 'test')
        self.assertEqual(result, 110)

    def test_decrease_reads_in_percent_hit_miunits(self):
        """ Check that min values are honoured """
        result = calculators.decrease_reads_in_units(20, 50, 15, 'test')
        self.assertEqual(result, 15)

    def test_decrease_reads_in_percent_more_than_100_units(self):
        """ Handle decreases of more that 100% """
        result = calculators.decrease_reads_in_units(20, 120, 1, 'test')
        self.assertEqual(result, 1)

    def test_decrease_writes_in_units(self):
        """ Ensure that a regular decrease works """
        result = calculators.decrease_writes_in_units(200, 90, 1, 'test')
        self.assertEqual(result, 110)

    def test_decrease_writes_in_units_hit_min_value(self):
        """ Check that min values are honoured """
        result = calculators.decrease_writes_in_units(20, 50, 15, 'test')
        self.assertEqual(result, 15)

    def test_increase_reads_in_percent(self):
        """ Ensure that a regular increase works """
        result = calculators.increase_reads_in_percent(200, 50, 400, 'test')
        self.assertEqual(result, 300)

    def test_increase_reads_in_percent_hit_max_value(self):
        """ Check that max values are honoured """
        result = calculators.increase_reads_in_percent(20, 50, 15, 'test')
        self.assertEqual(result, 15)

    def test_increase_reads_in_percent_more_than_100_percent(self):
        """ Handle increases of more that 100% """
        result = calculators.increase_reads_in_percent(20, 120, 1, 'test')
        self.assertEqual(result, 1)

    def test_increase_reads_in_percent_type_current_provisioning(self):
        """ Check that current_provisioning only takes an int """
        self.assertRaises(
            TypeError,
            calculators.increase_reads_in_percent,
            '100',
            90,
            1,
            'test')

    def test_increase_writes_in_percent(self):
        """ Ensure that a regular increase works """
        result = calculators.increase_writes_in_percent(200, 50, 400, 'test')
        self.assertEqual(result, 300)

    def test_increase_writes_in_percent_hit_max_value(self):
        """ Check that max values are honoured """
        result = calculators.increase_writes_in_percent(20, 50, 15, 'test')
        self.assertEqual(result, 15)

    def test_increase_writes_in_percent_more_than_100_percent(self):
        """ Handle increases of more that 100% """
        result = calculators.increase_writes_in_percent(20, 120, 1, 'test')
        self.assertEqual(result, 1)

    def test_increase_writes_in_percent_type_current_provisioning(self):
        """ Check that current_provisioning only takes an int """
        self.assertRaises(
            TypeError,
            calculators.increase_writes_in_percent,
            '100',
            90,
            1,
            'test')

    def test_increase_reads_in_units(self):
        """ Ensure that a regular increase works """
        result = calculators.increase_reads_in_units(200, 90, 300, 'test')
        self.assertEqual(result, 290)

    def test_increase_reads_in_units_hit_max_units(self):
        """ Check that max values are honoured """
        result = calculators.increase_reads_in_units(20, 50, 25, 'test')
        self.assertEqual(result, 25)

    def test_increase_writes_in_units(self):
        """ Ensure that a regular increase works """
        result = calculators.increase_writes_in_units(200, 90, 300, 'test')
        self.assertEqual(result, 290)

    def test_increase_writes_in_units_hit_max_value(self):
        """ Check that max values are honoured """
        result = calculators.increase_writes_in_units(20, 10, 25, 'test')
        self.assertEqual(result, 25)

if __name__ == '__main__':
    unittest.main(verbosity=2)
