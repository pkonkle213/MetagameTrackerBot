import unittest

import pandas as pd

import services.bar_chart_race_compat  # noqa: F401
import bar_chart_race as bcr


class BarChartRacePandasCompatibilityTests(unittest.TestCase):
    def test_wide_data_preparation_forward_fills_periods(self):
        frame = pd.DataFrame(
            {"Player A": [1, 3], "Player B": [2, 2]},
            index=pd.to_datetime(["2026-01-01", "2026-01-03"]),
        )

        values, ranks = bcr.prepare_wide_data(
            frame,
            steps_per_period=2,
        )

        self.assertEqual(len(values), 3)
        self.assertEqual(values.index[1], pd.Timestamp("2026-01-01"))
        self.assertEqual(ranks.shape, values.shape)

    def test_long_data_preparation_forward_fills_missing_values(self):
        frame = pd.DataFrame(
            [
                ("2026-01-01", "Player A", 1),
                ("2026-01-01", "Player B", 2),
                ("2026-01-02", "Player A", 3),
            ],
            columns=["Date", "Player", "Points"],
        )
        frame["Date"] = pd.to_datetime(frame["Date"])

        values, ranks = bcr.prepare_long_data(
            frame,
            index="Date",
            columns="Player",
            values="Points",
            steps_per_period=1,
        )

        self.assertEqual(values.loc[pd.Timestamp("2026-01-02"), "Player B"], 2)
        self.assertEqual(ranks.shape, values.shape)

    def test_chart_creation_succeeds_with_current_pandas(self):
        frame = pd.DataFrame(
            {"Player A": [1, 3], "Player B": [2, 2]},
            index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
        )

        result = bcr.bar_chart_race(
            df=frame,
            filename=None,
            n_bars=2,
            steps_per_period=1,
            period_length=100,
        )

        self.assertIsInstance(result, str)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
