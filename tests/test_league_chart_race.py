import tempfile
import unittest
from pathlib import Path

import pandas as pd

from services.league_chart_race import _rank_players, create_league_chart_race


class LeagueChartRaceTests(unittest.TestCase):
    def test_tied_players_keep_their_original_column_order(self):
        names, values = _rank_players(
            pd.Series([8, 8, 3]).to_numpy(),
            ["Player A", "Player B", "Player C"],
            2,
        )

        self.assertEqual(names, ["Player A", "Player B"])
        self.assertEqual(values.tolist(), [8, 8])

    def test_creates_mp4_leaderboard_video(self):
        frame = pd.DataFrame(
            {"Player A": [1, 5], "Player B": [3, 4], "Player C": [2, 6]},
            index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
        )

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "race.mp4"
            result = create_league_chart_race(
                frame,
                output,
                n_bars=2,
                steps_per_period=1,
                period_length=1000,
                figsize=(3, 2),
            )

            self.assertEqual(result, str(output))
            self.assertGreater(output.stat().st_size, 0)
            self.assertEqual(output.read_bytes()[4:8], b"ftyp")

    def test_rejects_empty_leaderboard(self):
        with self.assertRaisesRegex(ValueError, "without data"):
            create_league_chart_race(pd.DataFrame(), "race.mp4")

    def test_rejects_non_mp4_output(self):
        frame = pd.DataFrame({"Player A": [1]})
        with self.assertRaisesRegex(ValueError, "MP4"):
            create_league_chart_race(frame, "race.gif")


if __name__ == "__main__":
    unittest.main()
