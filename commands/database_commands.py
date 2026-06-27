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
            "Generating spreadsheet, please wait...", ephemeral=True
        )
        try:
            file = DatabaseCommandsDownload()
            await interaction.followup.send(
                "Here's the database!", file=file, ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(DatabaseCommands(bot), guilds=[Object(id=BOTGUILDID)])
