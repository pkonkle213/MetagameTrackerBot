import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings
from services.store_services import AssignMTSubmitterRole

TARGET_GUILDS = [settings.TESTSTOREGUILD.id]

class AssignMTSubitter(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='assignmtsubmitter',
  description='Assign the MTSubmitter role to a user')
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  @app_commands.guild_only()
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
    output = await AssignMTSubmitterRole(bot, user_id, guild_id)
    await interaction.followup.send(output)

async def setup(bot):
  await bot.add_cog(AssignMTSubitter(bot))