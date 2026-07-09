from checks import IsStore
from services.hub_invites_service import GetAllHubs
from discord import Interaction, app_commands
from discord.ext import commands
import settings

class Links(commands.Cog):
    """A group of commands for getting links"""

    def __init__(self, bot:commands.Bot):
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
        description="See All Hubs Connected To This Store",
    )
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    @IsStore()
    async def ViewAllData(self, interaction: Interaction):
        output = GetAllHubs(interaction)
        await interaction.response.send_message(output)

    @app_commands.command(
        name="get_sop",
        description="Display the url to get the SOP"
    )
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


async def setup(bot:commands.Bot):
    await bot.add_cog(Links(bot))
