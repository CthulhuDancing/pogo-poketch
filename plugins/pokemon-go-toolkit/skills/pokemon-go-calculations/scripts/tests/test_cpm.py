import unittest

from pogo_calc.shared.cpm import get_cpm, iter_levels, validate_level


class CpmTests(unittest.TestCase):
    def test_known_values(self):
        self.assertAlmostEqual(get_cpm(1), 0.094000000)
        self.assertAlmostEqual(get_cpm(40), 0.790300010)
        self.assertAlmostEqual(get_cpm(50), 0.840300010)
        self.assertAlmostEqual(get_cpm(51), 0.845300010)
        self.assertAlmostEqual(get_cpm(55), 0.865300000)

    def test_half_levels_only(self):
        with self.assertRaises(ValueError):
            validate_level(20.25)

    def test_inclusive_level_iteration(self):
        self.assertEqual(iter_levels(19.5, 21), (19.5, 20.0, 20.5, 21.0))


if __name__ == "__main__":
    unittest.main()
