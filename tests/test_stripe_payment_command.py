import os
import unittest

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

from commands.stripe_payment_command import StripePaymentCommands


class StripePaymentCommandTests(unittest.TestCase):
    def test_payment_choices_show_tier_specific_amounts_without_hub(self):
        commands = {
            command.name: command
            for command in StripePaymentCommands.__cog_app_commands__
        }

        self.assertEqual(set(commands), {"player", "store"})
        player_choices = {
            choice.name for choice in commands["player"].parameters[0].choices
        }
        store_choices = {
            choice.name for choice in commands["store"].parameters[0].choices
        }
        self.assertEqual(
            player_choices,
            {"Monthly ($5/month)", "Yearly ($50/year)"},
        )
        self.assertEqual(
            store_choices,
            {"Monthly ($10/month)", "Yearly ($100/year)"},
        )


if __name__ == "__main__":
    unittest.main()
