from discord import Interaction, TextChannel
from interaction_data import GetInteractionData
from database_connection import AddFormatMap, GetFormatsByGameId

def AddStoreFormatMap(interaction:Interaction, chosen_format):
  game, format, store, user_id = GetInteractionData(interaction,
                                                    store=True,
                                                    game=True)
  #TODO: I think this is double checking, DRY, so it should be refactored
  channel = interaction.channel
  if not isinstance(channel, TextChannel):
    return 'Cannot map a format to something that is not a channel'
  
  rows = AddFormatMap(store.DiscordId, chosen_format[0], channel.id)
  if rows is None:
    return 'Unable to add game map'
  return f'Success! This channel ({channel.name.title()}) is now mapped to {chosen_format[1].title()}'

def GetFormatOptions(interaction:Interaction):
  game, format, store, user_id = GetInteractionData(interaction,
                                                    store=True,
                                                    game=True)
  return GetFormatsByGameId(game.ID)