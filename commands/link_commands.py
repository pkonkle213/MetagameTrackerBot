from discord import Interaction
import settings
from discord.ext import commands
from discord import app_commands

class Links(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="getbot",
    description="Display the url to install the bot")
  @app_commands.guilds(settings.BOTGUILD.id)
  @app_commands.guild_only()
  async def GetBot(self, interaction: Interaction):
    await interaction.response.send_message(f'Here is the link to install the bot: {settings.MYBOTURL}')
  
  @app_commands.command(name='viewalldata',
    description='Get an invite to my data hub with more stores')
  async def ViewAllData(self, interaction: Interaction):
    await interaction.response.send_message(f'Here is the link to my data hub: {settings.DATAHUBINVITE}')
  
  @app_commands.command(name="getsop",
    description="Display the url to get the SOP")
  @app_commands.guild_only()
  @app_commands.guilds(settings.BOTGUILD.id)
  async def GetSOP(self, interaction: Interaction):
    await interaction.response.send_message(f'Here is the link to my living SOP: {settings.SOPURL}')
  
  @app_commands.command(name="feedback",
    description="Display the url to provide feedback on the bot")
  async def Feedback(self, interaction: Interaction):
    await interaction.response.send_message(f'Follow this link: {settings.FEEDBACKURL}')

async def setup(bot):
  await bot.add_cog(Links(bot))