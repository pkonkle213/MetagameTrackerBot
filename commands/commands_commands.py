from custom_errors import KnownError
from services.command_error_service import Error
from tuple_conversions import MTBRoles
from discord import Interaction, app_commands
from discord.ext import commands
from services.commands_services import GetCommandsHere, GetCommandsUser


class CommandCommands(commands.GroupCog, name="commands"):
    """A group of commands describing available commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="all", description="All commands available here")
    @app_commands.guild_only()
    async def CommandsHere(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        objects = interaction.extras.get("db_object")
        if not objects:
            raise KnownError("Insufficient information")
        guild = interaction.guild
        user = interaction.user
        output = await GetCommandsHere(objects, guild, user)
        await interaction.followup.send(output)

    @app_commands.command(name="for_me", description="All commands available for you")
    @app_commands.guild_only()
    async def CommandsUser(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        objects = interaction.extras.get("db_object")
        if not objects:
            raise KnownError("No interaction objects found")
        messages = await GetCommandsUser(
            objects, interaction.guild, interaction.user, self.bot.tree
        )
        for message in messages:
            await interaction.followup.send(message, ephemeral=True)

    @CommandsHere.error
    @CommandsUser.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(CommandCommands(bot))
