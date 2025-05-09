from discord import Interaction
from interaction_data import GetInteractionData, SplitInteractionData
from database_connection import AddFormatMap, GetFormatsByGameId

def AddStoreFormatMap(interaction:Interaction, chosen_format):
  discord_id, category_id, channel_id, user_id = SplitInteractionData(interaction)
  
  rows = AddFormatMap(discord_id, chosen_format[0], channel_id)
  if rows is None:
    return 'Unable to add game map'
  return f'Success! This channel ({channel_id}) is now mapped to {chosen_format[1].title()}'

def GetFormatOptions(interaction:Interaction):
  game, format, store, user_id = GetInteractionData(interaction,
                                                    store=True,
                                                    game=True)
  return GetFormatsByGameId(game.ID)