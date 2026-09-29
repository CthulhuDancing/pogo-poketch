import unittest

from pogo_calc.showcase import (
    calculate_displayed_showcase_range,
    calculate_showcase_score,
)


class ShowcaseScoreTests(unittest.TestCase):
    def test_theoretical_xxl_ceiling_is_1178(self):
        result = calculate_showcase_score(
            height_m=1.75,
            weight_kg=2.25,
            mean_height_m=1.0,
            mean_weight_kg=1.0,
            xxl_height_class=1.75,
            iv_sum=45,
            is_xxl=True,
        )
        self.assertAlmostEqual(result.height_points, 800.0)
        self.assertAlmostEqual(result.weight_points, 150.0)
        self.assertAlmostEqual(result.iv_points, 50.0)
        self.assertAlmostEqual(result.xxl_bonus, 178.0)
        self.assertAlmostEqual(result.total, 1178.0)

    def test_same_measurements_without_xxl_bonus_score_1000(self):
        result = calculate_showcase_score(
            height_m=2.0,
            weight_kg=2.5,
            mean_height_m=1.0,
            mean_weight_kg=1.0,
            xxl_height_class=2.0,
            iv_sum=45,
            is_xxl=False,
        )
        self.assertAlmostEqual(result.total, 1000.0)

    def test_squirtle_legacy_component_example(self):
        # Community worked example: 0.84 m / 16.54 kg, mean 0.5 m / 9 kg,
        # 1.75 XXL class and IV sum 20 gives ~912.7 before any XXL bonus.
        result = calculate_showcase_score(
            height_m=0.84,
            weight_kg=16.54,
            mean_height_m=0.5,
            mean_weight_kg=9.0,
            xxl_height_class=1.75,
            iv_sum=20,
            is_xxl=False,
        )
        self.assertAlmostEqual(result.total, 912.7407407407408, places=9)

    def test_displayed_range_brackets_central_estimate(self):
        result = calculate_displayed_showcase_range(
            displayed_height_m=1.87,
            displayed_weight_kg=30.0,
            mean_height_m=1.10,
            mean_weight_kg=19.0,
            xxl_height_class=1.75,
            iv_sum=30,
            is_xxl=True,
        )
        self.assertLess(result.minimum.total, result.estimate.total)
        self.assertLess(result.estimate.total, result.maximum.total)
        self.assertEqual(result.height_interval_m, (1.865, 1.875))
        self.assertEqual(result.weight_interval_kg, (29.995, 30.005))

    def test_rejects_unknown_xxl_height_class(self):
        with self.assertRaises(ValueError):
            calculate_showcase_score(
                height_m=1.0,
                weight_kg=1.0,
                mean_height_m=1.0,
                mean_weight_kg=1.0,
                xxl_height_class=1.8,
                iv_sum=45,
                is_xxl=True,
            )


if __name__ == "__main__":
    unittest.main()
