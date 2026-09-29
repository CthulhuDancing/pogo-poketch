import unittest

from pogo_calc.powerup_cost import calculate_power_up_cost, power_up_step_cost
from pogo_calc.shared.models import PowerUpForm


class PowerUpCostTests(unittest.TestCase):
    def test_regular_level_1_to_50_totals(self):
        cost = calculate_power_up_cost(1, 50)
        self.assertEqual(cost.power_ups, 98)
        self.assertEqual(cost.stardust, 520000)
        self.assertEqual(cost.candy, 304)
        self.assertEqual(cost.candy_xl, 296)

    def test_shadow_level_1_to_50_totals(self):
        cost = calculate_power_up_cost(1, 50, form=PowerUpForm.SHADOW)
        self.assertEqual(cost.stardust, 624000)
        self.assertEqual(cost.candy, 406)
        self.assertEqual(cost.candy_xl, 360)

    def test_lucky_halves_stardust_only(self):
        regular = calculate_power_up_cost(20, 40)
        lucky = calculate_power_up_cost(20, 40, lucky=True)
        self.assertEqual(lucky.stardust, regular.stardust // 2)
        self.assertEqual(lucky.candy, regular.candy)
        self.assertEqual(lucky.candy_xl, regular.candy_xl)

    def test_purified_lucky_stacks_stardust_reductions(self):
        step = power_up_step_cost(39, form=PowerUpForm.PURIFIED, lucky=True)
        self.assertEqual(step.stardust, 4500)
        self.assertEqual(step.candy, 14)

    def test_shadow_candy_rounds_up_per_step(self):
        step = power_up_step_cost(1, form=PowerUpForm.SHADOW)
        self.assertEqual(step.candy, 2)
        self.assertEqual(step.stardust, 240)

    def test_xl_begins_at_level_40(self):
        step = power_up_step_cost(40)
        self.assertEqual(step.candy, 0)
        self.assertEqual(step.candy_xl, 10)
        self.assertEqual(step.stardust, 10000)

    def test_cannot_power_above_50(self):
        with self.assertRaises(ValueError):
            calculate_power_up_cost(49.5, 50.5)

    def test_shadow_cannot_be_lucky(self):
        with self.assertRaises(ValueError):
            calculate_power_up_cost(20, 21, form=PowerUpForm.SHADOW, lucky=True)


if __name__ == "__main__":
    unittest.main()
