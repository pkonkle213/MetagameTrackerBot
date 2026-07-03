from interaction_objects import GetObjectsFromInteraction
from discord import Interaction

def GetAllHubsInvites(interaction: Interaction) -> None:
  objects = GetObjectsFromInteraction(interaction)
  
  ...