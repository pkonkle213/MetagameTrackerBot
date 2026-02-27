import json
import io
import csv
import discord
from discord.ext import commands
from discord import app_commands, Interaction
from services.command_error_service import Error


class JsonToCsv(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='json_to_csv',
                        description='Upload a JSON file and get a CSV with card names and USD prices')
  @app_commands.guild_only()
  async def JsonToCsvCommand(self,
                             interaction: Interaction,
                             json_file: discord.Attachment):
    """
    Parameters
    ----------
    json_file: Attachment
      A JSON file containing card data with name and prices fields
    """
    await interaction.response.defer(ephemeral=True)

    if not json_file.filename.endswith('.json'):
      await interaction.followup.send("Please upload a file with a '.json' extension.", ephemeral=True)
      return

    raw = await json_file.read()
    try:
      data = json.loads(raw.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
      await interaction.followup.send("The file contains invalid JSON. Please check the file and try again.", ephemeral=True)
      return

    if not isinstance(data, list):
      await interaction.followup.send("The JSON file must contain an array of objects.", ephemeral=True)
      return

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'usd'])

    count = 0
    for entry in data:
      if not isinstance(entry, dict):
        continue
      name = entry.get('name')
      if not name:
        continue
      prices = entry.get('prices')
      if not isinstance(prices, dict):
        continue
      usd = prices.get('usd')
      if usd is None:
        continue
      writer.writerow([name, usd])
      count += 1

    if count == 0:
      await interaction.followup.send("No entries with valid USD prices were found.", ephemeral=True)
      return

    output.seek(0)
    file = discord.File(fp=io.BytesIO(output.getvalue().encode('utf-8')),
                        filename='prices.csv')
    await interaction.followup.send(f"Found {count} entries with USD prices.", file=file, ephemeral=True)

  @JsonToCsvCommand.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)


async def setup(bot):
  await bot.add_cog(JsonToCsv(bot))
