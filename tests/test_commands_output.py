import unittest

from services.commands_services import _BuildCommandDescriptionMessages


class CommandDescriptionOutputTests(unittest.TestCase):
    def test_keeps_all_descriptions_across_discord_sized_messages(self):
        commands = [
            ("/one",),
            ("/two",),
            ("/three",),
        ]
        descriptions = {
            "/one": "First command description.",
            "/two": "Second command description. " * 100,
            "/three": "Third command description.",
        }

        messages = _BuildCommandDescriptionMessages(commands, descriptions)

        self.assertGreater(len(messages), 1)
        self.assertTrue(all(len(message) <= 2000 for message in messages))
        combined = "".join(message.partition("\n\n")[2] for message in messages)
        for description in descriptions.values():
            self.assertIn(description, combined)

    def test_includes_an_entry_for_each_command(self):
        commands = [("/one",), ("/two",)]
        descriptions = {"/one": "First description.", "/two": "Second description."}

        messages = _BuildCommandDescriptionMessages(commands, descriptions)
        output = "\n".join(messages)

        self.assertIn("/one\nFirst description.", output)
        self.assertIn("/two\nSecond description.", output)


if __name__ == "__main__":
    unittest.main()
