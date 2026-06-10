import settings
from discord import Interaction, app_commands, Object
from discord.ext import commands
from api_calls.moxfield_call import get_moxfield_decklist
from api_calls.mtg_parser import parse_mtg_decklist

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
    parse_mtg_decklist(deck_id)

    if False:
      decklist_url = f"https://www.moxfield.com/decks/{deck_id}"
      decklist = get_moxfield_decklist(decklist_url)
  
      print('----Decklist cards----')
      for card in decklist:
        print(card)
        
    await interaction.response.send_message("Decklist retrieved")

async def setup(bot:commands.Bot):
  await bot.add_cog(GetDecklist(bot))