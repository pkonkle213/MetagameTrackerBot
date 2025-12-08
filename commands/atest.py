import pytz
import typing
from datetime import datetime
import pathlib
import os

from discord import app_commands, Interaction, Attachment
import settings
import discord
from discord.ext import commands
from discord import app_commands
from services.object_storage_service import upload_file

TESTGUILD = [settings.TESTGUILDID]

class ATestCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="atest",
                        description="A test command")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TESTGUILD])
  async def ATest(self,
            interaction: Interaction,
            csv_file: typing.Optional[Attachment] = None):
    if csv_file is None:
      await interaction.response.send_message("No file uploaded")
    else:
      prev_filename = csv_file.filename
      timezone = pytz.timezone('US/Eastern')
      timestamp = datetime.now(timezone).strftime("%Y%m%d_%H%M%S")
      file_name = f"{timestamp}_{prev_filename}" if prev_filename != '' else f"{timestamp}_ModalInput"
  
      folder_name = f'{interaction.guild.id} - {interaction.guild.name}'
  
      BASE_DIR = pathlib.Path(__file__).parent.parent
      SAVE_DIRECTORY = BASE_DIR / "imported_files" / folder_name
      SAVE_DIRECTORY.mkdir(parents=True, exist_ok=True)
      save_path = os.path.join(SAVE_DIRECTORY, file_name)
      #save_path, file_name = BuildFilePath(interaction, csv_file.filename)
      await csv_file.save(pathlib.Path(save_path))
      upload_file(save_path,"/NewEventData/atest.csv")
      await interaction.response.send_message("File uploaded to object storage?")

async def setup(bot):
  await bot.add_cog(ATestCommand(bot))