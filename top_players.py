from discord import Interaction
from interaction_data import GetInteractionData

def GetTopPlayers(interaction:Interaction):
  game, format, store, user_id = GetInteractionData(interaction, game=True, store=True)
  
  