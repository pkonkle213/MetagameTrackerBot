import discord
from discord import ui
from discord import app_commands, Interaction
import settings
from discord.ext import commands
from services.btest import send_survey

TESTGUILD = [settings.TESTGUILDID]


class ATestCommand(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="atest", description="A test command")
  @app_commands.guild_only()
  @app_commands.guilds(
      *[discord.Object(id=guild_id) for guild_id in TESTGUILD])
  async def ATest(self, interaction: Interaction):
    #await interaction.response.send_message('Hello World!', ephemeral=True)
    await send_survey(interaction)


async def setup(bot):
  await bot.add_cog(ATestCommand(bot))
