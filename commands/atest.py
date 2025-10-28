import os
import pytz
import pathlib
import io
from datetime import datetime
import pandas as pd
import typing
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle
import discord
from services.date_functions import ConvertToDate
from data.metagame_data import GetMetagame
from tuple_conversions import Store, Game, Format
from discord.ext import commands
from discord import app_commands, Interaction
import settings

TARGET_GUILDS = [settings.TESTGUILDID]

BASE_DIR = pathlib.Path(__file__).parent.parent
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def TestingError(self,
                         interaction:Interaction,
                         error:app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send("1st attempt to catch the error")
    else:
      await interaction.followup.send("2nd attempt to catch the error")
 
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  #@app_commands.checks.has_role('MTSubmitter') #TODO: Find a way to check the role
  async def Testing(self,
                    interaction: discord.Interaction,
                    csv_file: typing.Optional[discord.Attachment] = None):
    await interaction.response.defer(ephemeral=True)
    try:
      if not csv_file:
        raise Exception("No file provided")
      if not csv_file.filename.endswith('.csv'):
        return await interaction.followup.send("Please upload a file with a '.csv' extension.")

      timezone = pytz.timezone('US/Eastern')
      timestamp = datetime.now(timezone).strftime("%Y%m%d_%H%M%S")
      file_name = f"{timestamp}_{csv_file.filename}"
      folder_name = f'{interaction.guild.id} - {interaction.guild.name}'
      
      SAVE_DIRECTORY = BASE_DIR / "imported_files" / folder_name
      SAVE_DIRECTORY.mkdir(parents=True, exist_ok=True)
      save_path = os.path.join(SAVE_DIRECTORY, file_name)

      csv_data = await csv_file.read()
      df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')), na_values=['FALSE','False'])
      
      await csv_file.save(pathlib.Path(save_path))

      round_number = int(csv_file.filename.split('-')[4])
      
      for index, row in df.iterrows():
        print('Table Number:', row['Table Number'])
        print('Player 1:', row['Player 1 First Name'] + ' ' + row['Player 1 Last Name'])
        print('Player 2:', row['Player 2 First Name'] + ' ' + row['Player 2 Last Name'])
        print('Player 1 wins', row['Player 1 Round Record'][0])
        print('Player 2 wins', row['Player 2 Round Record'][0])        
        
      await interaction.followup.send(f"File {csv_file.filename} uploaded successfully...kinda")
    except Exception as exception:
      await interaction.followup.send(f"An error occurred: {exception}")
  
      
  async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
        role_name = error.missing_role
        await interaction.response.send_message(
            f"You are missing the '{role_name}' role and cannot use this command.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)

async def setup(bot):
  await bot.add_cog(ATest(bot))
