import discord
from discord.ext import commands
from discord import app_commands, Interaction
from custom_errors import KnownError
from discord_messages import Error
import settings
from services.store_services import AssignMTSubmitterRole
from checks import isPhil

TARGET_GUILDS = [settings.TESTSTOREGUILD.id]

class AssignMTSubitter(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='assignmtsubmitter',
  description='Assign the MTSubmitter role to a user')
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  @app_commands.guild_only()
  @app_commands.check(isPhil)
  async def AssignMTSubmitter(self,
                              interaction: Interaction,
                              user_id: str,
                              guild_id: str):
    '''
    Parameters:
    ----------
    user_id: string
      The discord id of the user to assign the role to
    guild_id: string
      The discord id of the guild to assign the role in
    '''
    await interaction.response.defer()
    try:
      output = await AssignMTSubmitterRole(self.bot, user_id, guild_id)
      await interaction.followup.send(output)
    except KnownError as exception:
      await interaction.followup.send(exception.message)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(AssignMTSubitter(bot))