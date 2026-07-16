from interaction_objects import GetObjectsFromInteraction
from discord import Interaction, app_commands
from discord.ext import commands
from api_calls.archidekt_decklist import GetArchidektDecklist

class TestCommands(commands.Cog):
  def __init__(self, bot:commands.Bot):
    self.bot = bot

  @app_commands.command(name='archidekt_test',description='Testing')
  async def ArchidektTest(self, interaction:Interaction, url:str):
    await interaction.response.defer(thinking=True)
    await interaction.followup.send("Testing Archidekt Decklist")

    objects = GetObjectsFromInteraction(interaction)

    response = await GetArchidektDecklist(url, objects.format, 'Phil')
    await interaction.followup.send(response)


async def setup(bot:commands.Bot):
  await bot.add_cog(TestCommands(bot))
