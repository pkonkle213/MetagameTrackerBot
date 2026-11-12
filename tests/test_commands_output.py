import unittest

from output_builder import BuildTableOutput


class CommandOutputTests(unittest.TestCase):
    def test_table_output_splits_long_command_lists_within_discord_limit(self):
        commands = [
            (f"/command-{index}", f"Description for command {index}.")
            for index in range(100)
        ]

        messages = BuildTableOutput(
            "Commands available to you",
            ["Name", "Description"],
            commands,
        )

        self.assertGreater(len(messages), 1)
        self.assertTrue(all(len(message) <= 2000 for message in messages))
        combined = "\n".join(messages)
        for name, description in commands:
            with self.subTest(command=name):
                self.assertIn(name, combined)
                self.assertIn(description, combined)

    def test_table_output_includes_title_and_column_headers(self):
        messages = BuildTableOutput(
            "Commands available to you",
            ["Name", "Description"],
            [("/submit data", "Submit an event's data")],
        )

        self.assertIn("Commands available to you", messages[0])
        self.assertIn("Name", messages[0])
        self.assertIn("Description", messages[0])
        self.assertIn("/submit data", messages[0])
        self.assertIn("Submit an event's data", messages[0])


if __name__ == "__main__":
    unittest.main()
