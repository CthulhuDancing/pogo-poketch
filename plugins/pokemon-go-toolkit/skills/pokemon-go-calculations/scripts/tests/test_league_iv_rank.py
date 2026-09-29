import unittest

from pogo_calc.iv_rank import rank_all_iv_spreads, rank_iv_spread
from pogo_calc.league import find_league_endpoint, fits_cp_cap, is_level_eligible
from pogo_calc.shared.models import BaseStats, IVs


class LeagueTests(unittest.TestCase):
    def setUp(self):
        self.azumarill = BaseStats(112, 152, 225)

    def test_azumarill_rank_one_endpoint(self):
        endpoint = find_league_endpoint(
            self.azumarill,
            IVs(0, 15, 15),
            1500,
            max_level=50,
        )
        self.assertIsNotNone(endpoint)
        assert endpoint is not None
        self.assertEqual(endpoint.level, 45.5)
        self.assertEqual(endpoint.cp, 1499)
        self.assertEqual(endpoint.stats.hp, 196)

    def test_specific_level_eligibility(self):
        ivs = IVs(0, 15, 15)
        self.assertTrue(is_level_eligible(self.azumarill, ivs, 45.5, 1500))
        self.assertFalse(is_level_eligible(self.azumarill, ivs, 46.0, 1500))
        self.assertTrue(fits_cp_cap(1500, 1500))

    def test_no_endpoint_when_min_level_is_over_cap(self):
        huge = BaseStats(400, 400, 400)
        self.assertIsNone(
            find_league_endpoint(huge, IVs(15, 15, 15), 10, min_level=50, max_level=50)
        )


class IvRankTests(unittest.TestCase):
    def test_azumarill_rank_one_is_zero_fifteen_fifteen(self):
        azumarill = BaseStats(112, 152, 225)
        entry = rank_iv_spread(azumarill, IVs(0, 15, 15), 1500, max_level=50)
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.rank, 1)
        self.assertEqual(entry.candidate_count, 4096)
        self.assertAlmostEqual(entry.stat_product_percent, 100.0)
        self.assertAlmostEqual(entry.percentile, 100.0)

    def test_full_rank_list_is_monotonic(self):
        # This artificial species stays below the cap, so higher IVs should
        # eventually put the hundo at rank 1 at the shared max level.
        base = BaseStats(100, 100, 100)
        rankings = rank_all_iv_spreads(base, 1500, max_level=50)
        self.assertEqual(len(rankings), 4096)
        self.assertEqual(rankings[0].ivs, IVs(15, 15, 15))
        self.assertEqual(rankings[0].rank, 1)
        self.assertEqual(rankings[-1].rank, 4096)
        products = [entry.endpoint.stats.stat_product for entry in rankings]
        self.assertTrue(all(a >= b for a, b in zip(products, products[1:])))

    def test_iv_floor_changes_candidate_pool(self):
        base = BaseStats(100, 100, 100)
        rankings = rank_all_iv_spreads(base, 1500, iv_floor=10, iv_ceiling=15)
        self.assertEqual(len(rankings), 6**3)
        self.assertTrue(all(entry.ivs.attack >= 10 for entry in rankings))


if __name__ == "__main__":
    unittest.main()
