import discord
from discord.ext import commands
import settings
from timedposts.automated_updates import UpdateDataGuild

TARGET_GUILDS = [settings.BOTGUILD.id]

class ForceDataGuildUpdate(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @discord.app_commands.command(name="forceupdate",
                                description="Force an update of the data guild")
  @discord.app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def ForceUpdate(self, interaction: discord.Interaction):
    await interaction.response.defer()
    try:
      await UpdateDataGuild(self.bot)
      await interaction.followup.send("Data guild updated!")
    except Exception as exception:
      await interaction.followup.send(f"Error updating data guild: {exception}", ephemeral=True)

async def setup(bot):
  await bot.add_cog(ForceDataGuildUpdate(bot))