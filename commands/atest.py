import discord
from discord.ext import commands
from discord import app_commands, Interaction
from data_translation import ConvertMessageToData
from services.date_functions import ConvertToDate
import settings
from checks import isPhil
from services.store_services import NewStoreRegistration
from tuple_conversions import Data, Format, Game, Store

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  """
  @commands.Cog.listener()
  async def TestingError(self, interaction:Interaction, error:app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send("1st attempt to catch the error")
    else:
      await interaction.followup.send("2nd attempt to catch the error")
  """
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  #@app_commands.checks.has_role('MTSubmitter')
  async def Testing(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    message = """1
Tobin Rainey
1–0–0
20
James Bell
0–1–0
2
Phillip Konkle
0–1–0
02
Eric Satre
1–0–0
3
Adrian Dorogov
1–0–0
21
Collin Greter
0–1–0
4
Joe Weber
0–1–0
02
m grafton
1–0–0"""
    print('Message:', message)
    date_obj = "9/9/2025"
    game = Game(1, 'MAGIC', True)
    data, errors = ConvertMessageToData(interaction, message, game)
    print('Data:', data)
    print('Errors:', errors)
    if data is None:
      print('Freaking out, data is None')
    else:
      print('Data type:', type(data[0]))

    format = Format(1, 'PAUPER', ConvertToDate('1/1/2025'), False)
    store = Store(0,'Hi','Hi',1,'Phil',True,True)
    user_id = 1

    date = ConvertToDate(date_obj)
    event = 
    
    await interaction.followup.send("Tested!")
"""
  @Testing.error
  async def OtherError(self, interaction:Interaction, error:app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send("3rd attempt to catch the error")
    else:
      await interaction.followup.send("4th attempt to catch the error")
    """
async def setup(bot):
  await bot.add_cog(ATest(bot))
