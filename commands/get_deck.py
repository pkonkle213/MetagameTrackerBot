from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction
from services.determine_archetype_service import GetMoxfieldArchetype
import settings
from discord import Interaction, app_commands, Object
from discord.ext import commands
from api_calls.moxfield_call import get_moxfield_decklist

class GetDecklist(commands.Cog):
  def __init__(self, bot:commands.Bot):
    self.bot = bot

  @app_commands.command(
    name="get_decklist",
    description="Get a decklist from moxfield"
  )
  async def Decklist(
    self, interaction: Interaction, deck_id:str
  ):
    objects = GetObjectsFromInteraction(interaction)
    if not objects.format:
      raise KnownError('Needs a format')
    test = await GetMoxfieldArchetype(deck_id, objects.format)
        
    await interaction.response.send_message("Decklist retrieved")

async def setup(bot:commands.Bot):
  await bot.add_cog(GetDecklist(bot))