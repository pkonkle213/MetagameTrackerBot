import json
import requests
import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  #@app_commands.checks.has_role('MTSubmitter')
  async def Testing(self,
                    interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    """
    api_url = 'https://melee.gg/api/tournament/list'
    username = settings.MELEE_CLIENTID
    password = settings.MELEE_CLIENTSECRET
    """
    json_path = '_nonfunctioning/example_response.json'
    with open(json_path, 'r') as file:
      response = json.load(file)
    matches = response['Content']

    print('DateCreated:', response['Content'][0]['DateCreated'])
    """
    for match in matches:
      print("Round number:", match['RoundDescription'][6:])
      print("Table number:", match['TableNumberDescription'])
      print("Player 1 name:", match['Competitors'][0]['Team']['Players'][0]['DisplayName'])
      print("Player 1 game wins:", match['Competitors'][0]['GameWins'])
      p1byes = match['Competitors'][0]['GameByes']
      if p1byes > 0:
        print("Player 1 byes:", match['Competitors'][0]['GameByes'])
      else:
        print("Player 2 name:", match['Competitors'][1]['Team']['Players'][0]['DisplayName'])
        print("Player 2 game wins:", match['Competitors'][1]['GameWins'])    
    """
    await interaction.followup.send("Testing.")

  @Testing.error
  async def on_tree_error(self,
                          interaction: Interaction,
                          error: app_commands.AppCommandError):
    await interaction.response.send_message(str(error))

async def setup(bot):
  await bot.add_cog(ATest(bot))
