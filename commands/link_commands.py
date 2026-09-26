from services.command_error_service import Error
from checks import IsStore
from services.hub_invites_service import GetConnectedHubs
from discord import Interaction, app_commands
from discord.ext import commands
import settings


class Links(commands.Cog):
    """A group of commands for getting links"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="get_bot", description="Display the url to install the bot"
    )
    @app_commands.guilds(settings.BOTGUILDID)
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def GetBot(self, interaction: Interaction):
        await interaction.response.send_message(
            f"Here is the link to install the bot: {settings.MYBOTURL}"
        )

    @app_commands.command(
        name="view_hubs",
        description="See all hubs connected to this store, game, and/or format",
    )
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    @IsStore()
    async def ViewHubInvites(self, interaction: Interaction):
        output = await GetConnectedHubs(interaction)
        await interaction.response.send_message(output)

    @app_commands.command(name="get_sop", description="Display the url to get the SOP")
    @app_commands.guild_only()
    @app_commands.guilds(settings.BOTGUILDID)
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def GetSOP(self, interaction: Interaction):
        await interaction.response.send_message(
            f"Here is the link to my living SOP: {settings.SOPURL}"
        )

    @app_commands.command(
        name="feedback", description="Display the url to provide feedback on the bot"
    )
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def Feedback(self, interaction: Interaction):
        await interaction.response.send_message(
            f"Follow this link: {settings.FEEDBACKURL}"
        )

    @ViewHubInvites.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(Links(bot))
