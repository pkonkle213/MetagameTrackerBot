import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import discord

for environment_key, default_value in {
    "DATABASE_URL": "postgresql://test:test@localhost/test",
    "DISCORD_TOKEN": "test-token",
    "BOT_GUILD_ID": "1",
    "DATA_GUILD_ID": "2",
    "FIVE6_GUILD_ID": "3",
    "BOT_ERROR_ID": "4",
    "BOT_CLAIMSTREAM_ID": "5",
    "BOT_LOG_CHANNELID": "6",
    "BOT_URL_INSTALL": "https://example.com/install",
    "BOT_URL_SOP": "https://example.com/sop",
    "BOT_URL_FEEDBACK": "https://example.com/feedback",
    "PHIL_USERID": "7",
}.items():
    os.environ.setdefault(environment_key, default_value)

from commands import assign_roles_command
from tuple_conversions import MTBRoles


class AssignRolesCommandTests(unittest.IsolatedAsyncioTestCase):
    def test_parses_large_discord_id_from_text(self):
        self.assertEqual(
            assign_roles_command.parse_discord_id("  1234567890123456789  "),
            1234567890123456789,
        )

    def test_rejects_non_numeric_discord_id_text(self):
        for value in ("", "abc123", "-123", "12.3"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "digits only"):
                    assign_roles_command.parse_discord_id(value)

    async def test_access_check_requires_owner_and_bot_guild(self):
        interaction = SimpleNamespace(user=SimpleNamespace(id=7), guild_id=1)

        with patch.multiple(
            assign_roles_command.settings, PHILID=7, BOTGUILDID=1
        ):
            self.assertTrue(
                await assign_roles_command._is_bot_owner_in_bot_guild(interaction)
            )

            for user_id, guild_id in [(8, 1), (7, 2)]:
                with self.subTest(user_id=user_id, guild_id=guild_id):
                    interaction.user.id = user_id
                    interaction.guild_id = guild_id
                    with self.assertRaises(discord.app_commands.CheckFailure):
                        await assign_roles_command._is_bot_owner_in_bot_guild(
                            interaction
                        )

    async def test_assigns_both_roles_to_the_selected_guild_member(self):
        submitter_role = SimpleNamespace(name=MTBRoles.MTSubmitter.name)
        store_role = SimpleNamespace(name=MTBRoles.MTStore.name)
        member = SimpleNamespace(mention="<@42>", add_roles=AsyncMock())
        guild = SimpleNamespace(
            roles=[submitter_role, store_role],
            fetch_member=AsyncMock(return_value=member),
        )

        assigned_member = await assign_roles_command.assign_mt_roles(guild, 42, 7)

        self.assertIs(assigned_member, member)
        guild.fetch_member.assert_awaited_once_with(42)
        member.add_roles.assert_awaited_once_with(
            submitter_role,
            store_role,
            reason="Role assignment requested by Discord user 7",
        )

    async def test_reports_missing_roles_without_assigning_anything(self):
        guild = SimpleNamespace(roles=[], fetch_member=AsyncMock())

        with self.assertRaisesRegex(
            ValueError, "MTSubmitter, MTStore"
        ):
            await assign_roles_command.assign_mt_roles(guild, 42, 7)

        guild.fetch_member.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
