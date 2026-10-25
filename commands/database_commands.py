from discord.ext import commands
from discord import app_commands, Interaction, Object
from checks import isPhil
from data.database_commands_data import DatabaseCommandsDownload
from settings import BOTGUILDID


class DatabaseCommands(commands.GroupCog, name="database"):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name="download", description="Download the database")
    @app_commands.check(isPhil)
    async def DownloadDatabase(self, interaction: Interaction):
        await interaction.response.send_message(
            "Generating database export archives, please wait...", ephemeral=True
        )
        try:
            with await DatabaseCommandsDownload() as export:
                total_parts = len(export.files)
                for start in range(0, total_parts, 10):
                    files = export.files[start : start + 10]
                    first_part = start + 1
                    last_part = start + len(files)
                    await interaction.followup.send(
                        content=(
                            f"Database export archives "
                            f"{first_part}-{last_part} of {total_parts}."
                        ),
                        files=files,
                        ephemeral=True,
                    )
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(DatabaseCommands(bot), guilds=[Object(id=BOTGUILDID)])
