import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from output_builder import BuildTableOutput
from services.commands_services import GetCommandsUser


class CommandsServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_for_me_uses_table_layout_with_personalized_command_rows(self):
        objects = SimpleNamespace(
            store=None,
            hub=None,
            game=None,
            format=None,
            region=None,
        )
        guild = SimpleNamespace(id=42, roles=[])
        user = SimpleNamespace(id=7, roles=[])
        rows = [
            ("/submit data", "Submit an event's data"),
            ("/commands all", ""),
        ]

        with (
            patch(
                "services.commands_services.GetUserCommands",
                new_callable=AsyncMock,
                return_value=rows,
            ),
            patch("services.commands_services.isMTSubmitter", return_value=False),
            patch("services.commands_services.isMTStore", return_value=False),
            patch("services.commands_services.apu.IsPaidUser", return_value=False),
            patch("services.commands_services.apu.IsPaidStore", return_value=False),
            patch("services.commands_services.apu.IsPaidHub", return_value=False),
        ):
            output = await GetCommandsUser(objects, guild, user)

        self.assertEqual(
            output,
            BuildTableOutput(
                "Commands available to you",
                ["Name", "Description"],
                [
                    ("/submit data", "Submit an event's data"),
                    ("/commands all", "No description"),
                ],
            ),
        )
        self.assertIn("/submit data", "\n".join(output))
        self.assertIn("Submit an event's data", "\n".join(output))
        self.assertIn("No description", "\n".join(output))


if __name__ == "__main__":
    unittest.main()
