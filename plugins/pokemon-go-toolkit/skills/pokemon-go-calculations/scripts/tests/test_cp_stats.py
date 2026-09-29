import unittest

from pogo_calc.cp import calculate_at_level, calculate_cp
from pogo_calc.shared.models import BaseStats, IVs
from pogo_calc.stats import calculate_effective_stats


class CpAndStatsTests(unittest.TestCase):
    def test_charizard_hundo_level_40(self):
        charizard = BaseStats(223, 173, 186)
        self.assertEqual(calculate_cp(charizard, IVs(15, 15, 15), 40), 2889)

    def test_mewtwo_hundo_level_50(self):
        mewtwo = BaseStats(300, 182, 214)
        self.assertEqual(calculate_cp(mewtwo, IVs(15, 15, 15), 50), 4724)

    def test_cp_has_minimum_of_10(self):
        tiny = BaseStats(1, 1, 1)
        self.assertEqual(calculate_cp(tiny, IVs(0, 0, 0), 1), 10)

    def test_effective_hp_has_minimum_of_10(self):
        tiny = BaseStats(1, 1, 1)
        stats = calculate_effective_stats(tiny, IVs(0, 0, 0), 1)
        self.assertEqual(stats.hp, 10)

    def test_combined_calculation_is_consistent(self):
        base = BaseStats(112, 152, 225)
        ivs = IVs(0, 15, 15)
        result = calculate_at_level(base, ivs, 45.5)
        self.assertEqual(result.cp, calculate_cp(base, ivs, 45.5))
        self.assertEqual(result.stats, calculate_effective_stats(base, ivs, 45.5))


if __name__ == "__main__":
    unittest.main()
